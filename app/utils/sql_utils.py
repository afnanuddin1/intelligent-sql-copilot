import hashlib
import sqlparse


def hash_query(sql: str) -> str:
    normalized = sqlparse.format(sql.strip().lower(), strip_comments=True, reindent=False)
    return hashlib.sha256(normalized.encode()).hexdigest()


def format_sql(sql: str) -> str:
    return sqlparse.format(sql, reindent=True, keyword_case="upper", identifier_case="lower")


def is_select_only(sql: str) -> bool:
    parsed = sqlparse.parse(sql.strip())
    if not parsed:
        return False
    for statement in parsed:
        if statement.get_type() != "SELECT":
            return False
    return True
