from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Intelligent SQL Copilot",
    description="Natural language to SQL with AI-powered optimization for flight data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
