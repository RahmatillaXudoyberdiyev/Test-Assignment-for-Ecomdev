from pydantic import BaseModel, ConfigDict


class DebtorRead(BaseModel):
    """Schema representing an outstanding monthly debtor."""

    student_id: int
    name: str
    phone_number: str
    group: str
    monthly_payment_amount: float
    total_paid: float
    debt: float

    model_config = ConfigDict(from_attributes=True)
