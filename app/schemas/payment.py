from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    """Base payment fields."""

    student_id: int = Field(..., gt=0, description="Target student ID")
    amount: float = Field(..., gt=0, description="Payment amount")


class PaymentCreate(PaymentBase):
    """Schema for submitting a payment record."""

    date: Optional[datetime] = Field(None, description="Payment timestamp; defaults to current UTC time")


class PaymentRead(PaymentBase):
    """Schema for serialized payment details."""

    id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
