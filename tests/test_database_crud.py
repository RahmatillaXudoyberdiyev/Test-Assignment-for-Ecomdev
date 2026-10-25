import pytest
from datetime import datetime, timezone
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base
from app.models.student import Student
from app.models.payment import Payment
from app.schemas.student import StudentCreate, StudentUpdate
from app.schemas.payment import PaymentCreate
from app.crud.student import (
    create_student,
    get_student_by_id,
    list_students,
    update_student,
    delete_student,
)
from app.crud.payment import create_payment, list_payments_by_student
from app.crud.debtor import get_monthly_debtors


@pytest.fixture
async def async_session():
    """Create in-memory SQLite database session for testing."""
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
async def test_student_crud(async_session: AsyncSession):
    """Verify Student creation, retrieval, updating, and deletion."""
    student_in = StudentCreate(
        name="John Doe",
        phone_number="+998901234567",
        group="Python-101",
        monthly_payment_amount=500000.0,
    )
    student = await create_student(async_session, student_in)
    assert student.id is not None
    assert student.name == "John Doe"

    fetched = await get_student_by_id(async_session, student.id)
    assert fetched is not None
    assert fetched.name == "John Doe"

    all_students = await list_students(async_session)
    assert len(all_students) == 1

    updated = await update_student(
        async_session,
        student,
        StudentUpdate(monthly_payment_amount=600000.0),
    )
    assert updated.monthly_payment_amount == 600000.0

    deleted = await delete_student(async_session, updated)
    assert deleted is True

    fetched_after_delete = await get_student_by_id(async_session, student.id)
    assert fetched_after_delete is None


@pytest.mark.asyncio
async def test_payment_and_debtor_calculation(async_session: AsyncSession):
    """Verify payment logging and monthly debtor identification."""
    student_a = await create_student(
        async_session,
        StudentCreate(
            name="Alice Smith",
            phone_number="+998901112233",
            group="Web-Dev",
            monthly_payment_amount=500000.0,
        ),
    )
    student_b = await create_student(
        async_session,
        StudentCreate(
            name="Bob Brown",
            phone_number="+998904445566",
            group="Web-Dev",
            monthly_payment_amount=400000.0,
        ),
    )
    student_c = await create_student(
        async_session,
        StudentCreate(
            name="Charlie Green",
            phone_number="+998907778899",
            group="Design",
            monthly_payment_amount=300000.0,
        ),
    )

    now = datetime.now(timezone.utc)
    target_month = now.strftime("%Y-%m")

    # Alice pays partial (200k out of 500k)
    await create_payment(
        async_session,
        PaymentCreate(student_id=student_a.id, amount=200000.0, date=now),
    )

    # Bob pays in full (400k out of 400k)
    await create_payment(
        async_session,
        PaymentCreate(student_id=student_b.id, amount=400000.0, date=now),
    )

    # Charlie paid nothing

    # Alice payments history
    alice_payments = await list_payments_by_student(async_session, student_a.id)
    assert len(alice_payments) == 1
    assert alice_payments[0].amount == 200000.0

    # Calculate debtors
    debtors = await get_monthly_debtors(async_session, month_str=target_month)
    assert len(debtors) == 2

    debtor_ids = {d.student_id: d for d in debtors}
    assert student_a.id in debtor_ids
    assert student_c.id in debtor_ids
    assert student_b.id not in debtor_ids

    assert debtor_ids[student_a.id].debt == 300000.0
    assert debtor_ids[student_a.id].total_paid == 200000.0

    assert debtor_ids[student_c.id].debt == 300000.0
    assert debtor_ids[student_c.id].total_paid == 0.0
