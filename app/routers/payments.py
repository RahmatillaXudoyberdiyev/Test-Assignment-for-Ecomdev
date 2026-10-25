import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.crud.student import get_student_by_id
from app.crud.payment import create_payment, list_payments_by_student
from app.schemas.payment import PaymentCreate, PaymentRead

logger = logging.getLogger("app.routers.payments")
router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def add_payment(
    payment_in: PaymentCreate,
    session: AsyncSession = Depends(get_db_session),
) -> PaymentRead:
    """Record a tuition payment for a student."""
    logger.info("HTTP POST /payments requested: student_id=%d, amount=%.2f", payment_in.student_id, payment_in.amount)
    try:
        student = await get_student_by_id(session=session, student_id=payment_in.student_id)
        if not student:
            logger.warning("HTTP POST /payments rejected: Student with ID %d not found", payment_in.student_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {payment_in.student_id} not found",
            )
        payment = await create_payment(session=session, payment_in=payment_in)
        return payment
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("HTTP POST /payments failed: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not record payment: {str(error)}",
        )


@router.get("/student/{student_id}", response_model=List[PaymentRead])
async def get_payments_for_student(
    student_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> List[PaymentRead]:
    """Retrieve all payment records for a given student."""
    logger.debug("HTTP GET /payments/student/%d requested", student_id)
    try:
        student = await get_student_by_id(session=session, student_id=student_id)
        if not student:
            logger.warning("HTTP GET /payments/student/%d rejected: Student not found", student_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found",
            )
        payments = await list_payments_by_student(session=session, student_id=student_id)
        return payments
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("HTTP GET /payments/student/%d failed: %s", student_id, error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve payments: {str(error)}",
        )
