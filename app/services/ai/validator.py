import sqlparse

FORBIDDEN = ["INSERT","UPDATE","DELETE","DROP","CREATE","ALTER",
             "TRUNCATE","GRANT","REVOKE","EXECUTE","CALL","DO"]


def validate_sql(sql: str) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "Empty SQL"
    if not sql.upper().strip().startswith("SELECT"):
        return False, "Only SELECT queries are allowed"
    tokens = [str(t).upper() for t in sqlparse.parse(sql)[0].flatten()]
    for kw in FORBIDDEN:
        if kw in tokens:
            return False, f"Forbidden keyword: {kw}"
    if "--" in sql or "/*" in sql:
        return False, "SQL comments not allowed"
    if sql.count(";") > 1:
        return False, "Multiple statements not allowed"
    return True, ""
