from sqlalchemy import text
from app.db.session import sync_engine

_schema_cache: str | None = None


def get_schema_context() -> str:
    with sync_engine.connect() as conn:
        tables_result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        tables = [r[0] for r in tables_result]

        parts = []
        for table in tables:
            cols = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :t
                ORDER BY ordinal_position
            """), {"t": table}).fetchall()

            fks = conn.execute(text("""
                SELECT kcu.column_name, ccu.table_name, ccu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = :t
            """), {"t": table}).fetchall()

            col_lines = [f"  {c[0]} ({c[1]}, {'nullable' if c[2]=='YES' else 'not null'})" for c in cols]
            fk_lines  = [f"  FK: {f[0]} -> {f[1]}.{f[2]}" for f in fks]
            parts.append("TABLE: " + table + "\n" + "\n".join(col_lines + fk_lines))

        views = conn.execute(text(
            "SELECT table_name FROM information_schema.views WHERE table_schema='public'"
        )).fetchall()
        if views:
            parts.append("VIEWS: " + ", ".join(v[0] for v in views))

        return "\n\n".join(parts)


def get_cached_schema() -> str:
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = get_schema_context()
    return _schema_cache


def invalidate_schema_cache():
    global _schema_cache
    _schema_cache = None
