import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select, func

from app.database import Base
from app.models.student import Student
from app.models.payment import Payment
from app.seed import seed_initial_data


@pytest.fixture
async def seed_test_session():
    """Create in-memory SQLite database session for testing seed functionality."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_seed_initial_data(seed_test_session: AsyncSession):
    """Verify that seed_initial_data populates records only on an empty database."""
    # First execution: should populate sample data
    await seed_initial_data(seed_test_session)

    students_stmt = select(func.count(Student.id))
    students_count = (await seed_test_session.execute(students_stmt)).scalar_one()
    assert students_count == 5

    payments_stmt = select(func.count(Payment.id))
    payments_count = (await seed_test_session.execute(payments_stmt)).scalar_one()
    assert payments_count == 4

    # Second execution: should detect existing data and skip without duplicating
    await seed_initial_data(seed_test_session)

    students_count_after = (await seed_test_session.execute(students_stmt)).scalar_one()
    assert students_count_after == 5
