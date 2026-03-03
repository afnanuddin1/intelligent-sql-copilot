from fastapi import APIRouter
from app.services.database.schema_inspector import get_cached_schema, invalidate_schema_cache

router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("/context")
async def get_schema():
    return {"schema": get_cached_schema()}


@router.post("/refresh")
async def refresh_schema():
    invalidate_schema_cache()
    return {"message": "Schema cache cleared"}
