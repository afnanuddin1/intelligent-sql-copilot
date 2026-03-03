from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.query import QueryRequest, QueryResponse, QueryHistoryItem
from app.services.query_orchestrator import run_query_pipeline

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/run", response_model=QueryResponse)
async def run_query(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await run_query_pipeline(
            natural_language=request.natural_language,
            db=db,
            force_refresh=request.force_refresh,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/history", response_model=list[QueryHistoryItem])
async def get_history(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT id, natural_language, generated_sql, execution_time_ms,
               rows_returned, had_seq_scan, was_cached, created_at
        FROM query_logs ORDER BY created_at DESC LIMIT :limit OFFSET :offset
    """), {"limit": limit, "offset": offset})
    rows = result.fetchall()
    keys = result.keys()
    return [QueryHistoryItem(**dict(zip(keys, row))) for row in rows]


@router.get("/history/{query_id}")
async def get_query_detail(query_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM query_logs WHERE id = :id"), {"id": query_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Query log not found")
    return dict(zip(result.keys(), row))
