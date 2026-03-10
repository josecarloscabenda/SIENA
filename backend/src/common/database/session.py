"""Database session management."""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.common.database.base import Base  # noqa: F401

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://siena:siena@localhost:5432/siena",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("APP_ENV") == "development",
    pool_size=20,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
