from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    """Base student data fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Full name of student")
    phone_number: str = Field(..., min_length=5, max_length=32, description="Contact phone number")
    group: str = Field(..., min_length=1, max_length=64, description="Student's educational group")
    monthly_payment_amount: float = Field(..., gt=0, description="Agreed monthly tuition amount")


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating an existing student."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=5, max_length=32)
    group: Optional[str] = Field(None, min_length=1, max_length=64)
    monthly_payment_amount: Optional[float] = Field(None, gt=0)


class StudentRead(StudentBase):
    """Schema for returning student information."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
