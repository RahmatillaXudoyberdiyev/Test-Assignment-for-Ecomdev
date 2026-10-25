from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.crud.student import get_student_by_id
from app.crud.payment import create_payment, list_payments_by_student
from app.schemas.payment import PaymentCreate, PaymentRead

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def add_payment(
    payment_in: PaymentCreate,
    session: AsyncSession = Depends(get_db_session),
) -> PaymentRead:
    """Record a tuition payment for a student."""
    student = await get_student_by_id(session=session, student_id=payment_in.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {payment_in.student_id} not found",
        )
    try:
        payment = await create_payment(session=session, payment_in=payment_in)
        return payment
    except Exception as error:
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
    student = await get_student_by_id(session=session, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    try:
        return await list_payments_by_student(session=session, student_id=student_id)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve payments: {str(error)}",
        )
