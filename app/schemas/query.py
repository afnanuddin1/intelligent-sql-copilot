from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class QueryRequest(BaseModel):
    natural_language: str
    force_refresh: bool = False


class ExplainNode(BaseModel):
    node_type: str
    relation: Optional[str] = None
    total_cost: float
    actual_rows: Optional[int] = None
    is_seq_scan: bool = False


class ExplainAnalysis(BaseModel):
    total_cost: float
    planning_time_ms: float
    execution_time_ms: float
    nodes: list[ExplainNode]
    seq_scans: list[str]


class OptimizationSuggestion(BaseModel):
    type: str
    table: Optional[str] = None
    columns: Optional[list[str]] = None
    reason: str
    ddl: Optional[str] = None


class Optimizations(BaseModel):
    severity: str
    suggestions: list[OptimizationSuggestion]
    rewritten_sql: Optional[str] = None
    cost_comparison: Optional[dict] = None


class QueryResults(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    total_rows: int


class QueryResponse(BaseModel):
    query_id: Optional[int] = None
    natural_language: str
    generated_sql: str
    execution_time_ms: float
    was_cached: bool
    results: QueryResults
    explain_analysis: Optional[ExplainAnalysis] = None
    optimizations: Optional[Optimizations] = None
    created_at: datetime


class QueryHistoryItem(BaseModel):
    id: int
    natural_language: str
    generated_sql: str
    execution_time_ms: Optional[float] = None
    rows_returned: Optional[int] = None
    had_seq_scan: bool
    was_cached: bool
    created_at: datetime

    class Config:
        from_attributes = True
