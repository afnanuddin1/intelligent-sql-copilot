from fastapi import APIRouter
from app.api.v1 import query, schema

router = APIRouter(prefix="/api/v1")
router.include_router(query.router)
router.include_router(schema.router)
