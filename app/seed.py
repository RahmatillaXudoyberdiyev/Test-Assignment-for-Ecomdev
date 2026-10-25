import logging
from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.models.payment import Payment

logger = logging.getLogger("app.seed")


async def seed_initial_data(session: AsyncSession) -> None:
    """Pre-populate database with test students and payments on first run."""
    try:
        count_stmt = select(func.count(Student.id))
        result = await session.execute(count_stmt)
        student_count = result.scalar_one_or_none() or 0

        if student_count > 0:
            logger.info("Database already contains %d students. Skipping auto-seed.", student_count)
            return

        logger.info("Empty database detected. Starting initial test data pre-population...")
        now = datetime.now(timezone.utc)

        sample_students = [
            Student(
                name="Алексей Смирнов",
                phone_number="+998901112233",
                group="Python-Backend",
                monthly_payment_amount=1000000.0,
            ),
            Student(
                name="Мадина Юсупова",
                phone_number="+998902223344",
                group="Frontend-React",
                monthly_payment_amount=800000.0,
            ),
            Student(
                name="Дмитрий Ким",
                phone_number="+998903334455",
                group="Data-Science",
                monthly_payment_amount=1200000.0,
            ),
            Student(
                name="Нигора Рахимова",
                phone_number="+998904445566",
                group="UI-UX-Design",
                monthly_payment_amount=700000.0,
            ),
            Student(
                name="Сардор Алиев",
                phone_number="+998905556677",
                group="Python-Backend",
                monthly_payment_amount=1000000.0,
            ),
        ]

        session.add_all(sample_students)
        await session.commit()

        for s in sample_students:
            await session.refresh(s)

        sample_payments = [
            Payment(
                student_id=sample_students[0].id,
                amount=400000.0,
                date=now,
            ),
            Payment(
                student_id=sample_students[1].id,
                amount=800000.0,
                date=now,
            ),
            Payment(
                student_id=sample_students[3].id,
                amount=700000.0,
                date=now,
            ),
            Payment(
                student_id=sample_students[4].id,
                amount=500000.0,
                date=now,
            ),
        ]

        session.add_all(sample_payments)
        await session.commit()
        logger.info("Auto-seed completed: 5 sample students and 4 initial payments created for testing.")
    except Exception as error:
        await session.rollback()
        logger.exception("Failed to execute database auto-seed: %s", error)
        raise
