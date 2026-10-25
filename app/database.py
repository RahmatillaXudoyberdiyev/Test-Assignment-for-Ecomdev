from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


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
            yield session
        except Exception as error:
            await session.rollback()
            print(f"[Database Error] Session rolled back: {error}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all database tables if they do not exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[Database] Tables initialized successfully.")
    except Exception as error:
        print(f"[Database Error] Failed to initialize tables: {error}")
        raise
