from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings

settings = get_settings()


async def execute_query(db: AsyncSession, sql: str) -> tuple[list[str], list[list]]:
    result = await db.execute(text(sql))
    columns = list(result.keys())
    rows = [list(row) for row in result.fetchmany(settings.max_result_rows)]
    return columns, rows


async def execute_explain(db: AsyncSession, sql: str) -> list:
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}"
    result = await db.execute(text(explain_sql))
    rows = result.fetchall()
    return rows[0][0] if rows else []
