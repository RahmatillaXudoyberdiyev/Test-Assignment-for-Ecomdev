import logging
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate

logger = logging.getLogger("app.crud.payment")


async def create_payment(session: AsyncSession, payment_in: PaymentCreate) -> Payment:
    """Record a payment entry for a student."""
    try:
        payment_date = payment_in.date or datetime.now(timezone.utc)
        logger.info("Registering payment: student_id=%d, amount=%.2f, date=%s", payment_in.student_id, payment_in.amount, payment_date)
        payment = Payment(
            student_id=payment_in.student_id,
            amount=payment_in.amount,
            date=payment_date,
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        logger.info("Payment saved successfully: payment_id=%d for student_id=%d", payment.id, payment.student_id)
        return payment
    except Exception as error:
        await session.rollback()
        logger.exception("Failed to record payment for student_id=%d: %s", payment_in.student_id, error)
        raise


async def list_payments_by_student(session: AsyncSession, student_id: int) -> List[Payment]:
    """Retrieve all payment records associated with a specific student."""
    try:
        logger.debug("Listing payments for student_id=%d", student_id)
        statement = (
            select(Payment)
            .where(Payment.student_id == student_id)
            .order_by(Payment.date.desc())
        )
        result = await session.execute(statement)
        payments = list(result.scalars().all())
        logger.debug("Retrieved %d payments for student_id=%d", len(payments), student_id)
        return payments
    except Exception as error:
        logger.exception("Failed to retrieve payments for student_id=%d: %s", student_id, error)
        raise
