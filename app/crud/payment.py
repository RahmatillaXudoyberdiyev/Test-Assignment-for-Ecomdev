from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate


async def create_payment(session: AsyncSession, payment_in: PaymentCreate) -> Payment:
    """Record a payment entry for a student."""
    try:
        payment_date = payment_in.date or datetime.now(timezone.utc)
        payment = Payment(
            student_id=payment_in.student_id,
            amount=payment_in.amount,
            date=payment_date,
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        print(f"[CRUD] Created payment: id={payment.id}, student_id={payment.student_id}, amount={payment.amount}")
        return payment
    except Exception as error:
        await session.rollback()
        print(f"[CRUD Error] Failed to create payment: {error}")
        raise


async def list_payments_by_student(session: AsyncSession, student_id: int) -> List[Payment]:
    """Retrieve all payment records associated with a specific student."""
    try:
        statement = (
            select(Payment)
            .where(Payment.student_id == student_id)
            .order_by(Payment.date.desc())
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    except Exception as error:
        print(f"[CRUD Error] Failed to list payments for student_id={student_id}: {error}")
        raise
