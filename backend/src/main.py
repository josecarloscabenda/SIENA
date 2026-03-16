"""SIENA — Sistema de Integração Educacional Nacional de Angola."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.common.database.session import engine
from src.modules.academico.api.router import router as academico_router
from src.modules.avaliacoes.api.import_router import router as avaliacoes_import_router
from src.modules.avaliacoes.api.router import router as avaliacoes_router
from src.modules.directory.api.import_router import router as directory_import_router
from src.modules.directory.api.router import router as directory_router
from src.modules.enrollment.api.router import router as enrollment_router
from src.modules.escolas.api.router import router as escolas_router
from src.modules.identity.api.router import router as identity_router

logger = logging.getLogger("siena")

# Redis client (global)
redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown events."""
    global redis_client

    # --- Startup ---
    logger.info("Starting SIENA backend...")

    # Test PostgreSQL connection
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        result.scalar()
    logger.info("PostgreSQL connection OK")

    # Connect to Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = aioredis.from_url(redis_url, decode_responses=True)
    await redis_client.ping()
    logger.info("Redis connection OK")

    yield

    # --- Shutdown ---
    if redis_client:
        await redis_client.aclose()
        logger.info("Redis connection closed")

    await engine.dispose()
    logger.info("PostgreSQL connection pool closed")


# Logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

app = FastAPI(
    title="SIENA",
    description="Sistema de Integração Educacional Nacional de Angola",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "siena"}


@app.get("/api/health/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check — verifica PostgreSQL e Redis."""
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    if redis_client:
        await redis_client.ping()

    return {"status": "ready"}


# --- Registar routers dos módulos ---
app.include_router(identity_router, prefix="/api/v1", tags=["Identity"])
app.include_router(escolas_router, prefix="/api/v1", tags=["Escolas"])
app.include_router(directory_router, prefix="/api/v1", tags=["Directory"])
app.include_router(enrollment_router, prefix="/api/v1", tags=["Enrollment"])
app.include_router(academico_router, prefix="/api/v1", tags=["Academico"])
app.include_router(avaliacoes_router, prefix="/api/v1", tags=["Avaliacoes"])
app.include_router(directory_import_router, prefix="/api/v1", tags=["Import"])
app.include_router(avaliacoes_import_router, prefix="/api/v1", tags=["Import"])
