import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import get_settings
from app.services.ai.nl_to_sql import generate_sql
from app.services.ai.optimizer import get_optimization_suggestions
from app.services.database.executor import execute_query, execute_explain
from app.services.database.explain_parser import parse_explain_output
from app.services.cache.redis_service import redis_service
from app.utils.sql_utils import hash_query, format_sql
from app.utils.timing import timer
from app.schemas.query import (
    QueryResponse, QueryResults, ExplainAnalysis,
    ExplainNode, Optimizations, OptimizationSuggestion,
)

settings = get_settings()


async def run_query_pipeline(
    natural_language: str,
    db: AsyncSession,
    force_refresh: bool = False,
) -> QueryResponse:

    # 1. Cache check
    cache_key = f"query:{hash_query(natural_language)}"
    if not force_refresh:
        cached = await redis_service.get(cache_key)
        if cached:
            cached["was_cached"] = True
            return QueryResponse(**cached)

    # 2. Generate SQL via AI
    sql = await generate_sql(natural_language)
    sql = format_sql(sql)
    sql_hash = hash_query(sql)

    # 3. EXPLAIN ANALYZE
    explain_raw  = await execute_explain(db, sql)
    explain_data = parse_explain_output(explain_raw)

    # 4. Execute query
    with timer() as t:
        columns, rows = await execute_query(db, sql)

    execution_time_ms = explain_data.get("execution_time_ms") or t["elapsed_ms"]

    # 5. Optimization suggestions
    suggestions_raw = await get_optimization_suggestions(
        sql=sql,
        total_cost=explain_data.get("total_cost", 0),
        execution_time_ms=execution_time_ms,
        seq_scans=explain_data.get("seq_scans", []),
        expensive_nodes=explain_data.get("expensive_nodes", []),
    )

    # 6. Build response
    explain_analysis = ExplainAnalysis(
        total_cost=explain_data.get("total_cost", 0),
        planning_time_ms=explain_data.get("planning_time_ms", 0),
        execution_time_ms=explain_data.get("execution_time_ms", 0),
        nodes=[ExplainNode(**n) for n in explain_data.get("nodes", [])],
        seq_scans=explain_data.get("seq_scans", []),
    ) if explain_data else None

    optimizations = Optimizations(
        severity=suggestions_raw.get("severity", "ok"),
        suggestions=[OptimizationSuggestion(**s) for s in suggestions_raw.get("suggestions", [])],
        rewritten_sql=suggestions_raw.get("rewritten_sql"),
        cost_comparison=suggestions_raw.get("cost_comparison"),
    ) if suggestions_raw else None

    now = datetime.now(timezone.utc)

    response = QueryResponse(
        natural_language=natural_language,
        generated_sql=sql,
        execution_time_ms=execution_time_ms,
        was_cached=False,
        results=QueryResults(columns=columns, rows=rows, total_rows=len(rows)),
        explain_analysis=explain_analysis,
        optimizations=optimizations,
        created_at=now,
    )

    # 7. Log to DB
    had_seq_scan = bool(explain_data.get("seq_scans"))
    await db.execute(text("""
        INSERT INTO query_logs
            (natural_language, generated_sql, sql_hash, execution_time_ms,
             total_cost, rows_returned, had_seq_scan, explain_output,
             suggestions, was_cached, created_at)
        VALUES
            (:nl, :sql, :hash, :exec_ms, :cost, :rows,
             :seq, :explain, :sugg, false, :now)
    """), {
        "nl": natural_language, "sql": sql, "hash": sql_hash,
        "exec_ms": execution_time_ms,
        "cost": explain_data.get("total_cost"),
        "rows": len(rows), "seq": had_seq_scan,
        "explain": json.dumps(explain_raw, default=str),
        "sugg": json.dumps(suggestions_raw, default=str),
        "now": now,
    })
    await db.commit()

    # 8. Cache result
    await redis_service.set(cache_key, response.model_dump(), ttl=settings.redis_ttl_results)

    return response
