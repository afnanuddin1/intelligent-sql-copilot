from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.config import get_settings
from app.db.seed import create_views

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_views()
    except Exception as e:
        print(f"Warning: could not create views on startup: {e}")
    yield


app = FastAPI(
    lifespan=lifespan,
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
