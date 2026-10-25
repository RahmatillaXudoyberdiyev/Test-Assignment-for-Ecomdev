import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.logger import setup_logging

logger = logging.getLogger("app.database")

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all models."""
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous database session for FastAPI dependency injection."""
    async with async_session_factory() as session:
        try:
            logger.debug("Database session opened.")
            yield session
        except Exception as error:
            logger.exception("Database session encountered an error; rolling back transaction: %s", error)
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Database session closed.")


async def init_db() -> None:
    """Create all database tables if they do not exist."""
    try:
        logger.info("Initializing database tables for engine: %s", settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified and initialized successfully.")
    except Exception as error:
        logger.exception("Failed to initialize database tables: %s", error)
        raise
