from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.payment import Payment


class Student(Base):
    """Student database model representing enrolled students."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)
    group: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    monthly_payment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
