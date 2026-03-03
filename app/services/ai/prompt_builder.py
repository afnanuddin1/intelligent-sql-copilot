from app.services.database.schema_inspector import get_cached_schema

SYSTEM_PROMPT = """
You are an expert PostgreSQL query writer for a flight database.
Convert natural language questions into correct, optimized SQL SELECT queries.

DATABASE SCHEMA:
{schema}

USE THESE VIEWS — DO NOT JOIN THEM WITH RAW TABLES:

vw_flight_summary columns (use this for all flight queries):
  id, flight_number, airline, airline_code, origin, origin_city, origin_country,
  destination, dest_city, dest_country, scheduled_dep, scheduled_arr, status,
  dep_delay_mins, arr_delay_mins, seats_available, seats_sold, base_price,
  aircraft_model, distance_km

vw_airline_stats columns (use this for airline ranking/stats queries):
  id, name, iata_code, country, alliance, total_flights, total_routes,
  avg_dep_delay, avg_arr_delay, cancelled_flights, avg_rating, total_reviews

EXAMPLE QUERIES:
- "flights going to France" -> SELECT * FROM vw_flight_summary WHERE dest_country ILIKE 'france' LIMIT 100;
- "airlines with most flights" -> SELECT name, total_flights FROM vw_airline_stats ORDER BY total_flights DESC LIMIT 10;
- "cancelled flights" -> SELECT * FROM vw_flight_summary WHERE status = 'cancelled' LIMIT 100;

RULES:
1. Only write SELECT statements. Never INSERT, UPDATE, DELETE, DROP or DDL.
2. ALWAYS use vw_flight_summary for flight queries. NEVER join it with raw tables.
3. ALWAYS use vw_airline_stats for airline stats. NEVER join it with raw tables.
4. Add ORDER BY when ranking is implied.
5. Add LIMIT when the question asks for top N — default LIMIT 100.
6. Use ILIKE for case-insensitive string matching.
7. Return ONLY the raw SQL query. NO explanation. NO markdown. NO backticks. NO comments.
"""

OPTIMIZATION_PROMPT = """
You are a PostgreSQL performance expert. Analyze this query execution and provide suggestions.

QUERY:
{sql}

EXPLAIN ANALYSIS:
- Total cost: {total_cost}
- Execution time: {execution_time_ms}ms
- Sequential scans on: {seq_scans}
- Expensive nodes: {expensive_nodes}

DATABASE SCHEMA:
{schema}

Respond ONLY with this exact JSON structure:
{{
  "severity": "ok|warning|critical",
  "suggestions": [
    {{
      "type": "missing_index|query_rewrite|schema_change",
      "table": "table_name",
      "columns": ["col1", "col2"],
      "reason": "why this helps",
      "ddl": "CREATE INDEX ... or null"
    }}
  ],
  "rewritten_sql": "optimized SQL or null",
  "cost_comparison": {{"original": {total_cost}, "estimated_rewritten": null}}
}}
"""


def build_nl_to_sql_prompt(natural_language: str) -> tuple[str, str]:
    schema = get_cached_schema()
    system = SYSTEM_PROMPT.format(schema=schema)
    user   = f"Convert this to SQL:\n{natural_language}"
    return system, user


def build_optimization_prompt(sql, total_cost, execution_time_ms, seq_scans, expensive_nodes) -> tuple[str, str]:
    schema = get_cached_schema()
    system = "You are a PostgreSQL performance expert. Respond with valid JSON only."
    user   = OPTIMIZATION_PROMPT.format(
        sql=sql, total_cost=total_cost,
        execution_time_ms=execution_time_ms,
        seq_scans=", ".join(seq_scans) or "none",
        expensive_nodes=", ".join(expensive_nodes) or "none",
        schema=schema,
    )
    return system, user
