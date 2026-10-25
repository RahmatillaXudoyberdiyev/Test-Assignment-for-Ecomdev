from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.models.payment import Payment
from app.schemas.debtor import DebtorRead


def parse_target_month_range(month_str: Optional[str] = None) -> Tuple[datetime, datetime, str]:
    """Parse YYYY-MM into start and end UTC timestamps."""
    now = datetime.now(timezone.utc)
    if not month_str:
        year = now.year
        month = now.month
        month_label = f"{year:04d}-{month:02d}"
    else:
        try:
            parts = month_str.strip().split("-")
            if len(parts) != 2:
                raise ValueError("Invalid format")
            year = int(parts[0])
            month = int(parts[1])
            if month < 1 or month > 12:
                raise ValueError("Invalid month value")
            month_label = f"{year:04d}-{month:02d}"
        except Exception as error:
            print(f"[Debtor] Invalid month string '{month_str}', fallback to current month: {error}")
            year = now.year
            month = now.month
            month_label = f"{year:04d}-{month:02d}"

    start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    return start_date, end_date, month_label


async def get_monthly_debtors(
    session: AsyncSession,
    month_str: Optional[str] = None,
) -> List[DebtorRead]:
    """Retrieve students who paid less than their agreed monthly fee for the given month."""
    try:
        start_date, end_date, _ = parse_target_month_range(month_str)

        # Using naive dates as secondary boundary check for SQLite date compatibility
        start_naive = start_date.replace(tzinfo=None)
        end_naive = end_date.replace(tzinfo=None)

        statement = (
            select(
                Student,
                func.coalesce(func.sum(Payment.amount), 0.0).label("total_paid"),
            )
            .outerjoin(
                Payment,
                (Payment.student_id == Student.id)
                & (
                    ((Payment.date >= start_date) & (Payment.date < end_date))
                    | ((Payment.date >= start_naive) & (Payment.date < end_naive))
                ),
            )
            .group_by(Student.id)
            .order_by(Student.id.asc())
        )

        result = await session.execute(statement)
        rows = result.all()

        debtors: List[DebtorRead] = []
        for student, total_paid in rows:
            paid = round(float(total_paid or 0.0), 2)
            monthly_due = round(float(student.monthly_payment_amount), 2)
            debt = round(monthly_due - paid, 2)

            if debt > 0:
                debtors.append(
                    DebtorRead(
                        student_id=student.id,
                        name=student.name,
                        phone_number=student.phone_number,
                        group=student.group,
                        monthly_payment_amount=monthly_due,
                        total_paid=paid,
                        debt=debt,
                    )
                )

        print(f"[Debtor] Found {len(debtors)} debtors for period {start_date.strftime('%Y-%m')}")
        return debtors
    except Exception as error:
        print(f"[Debtor Error] Failed to compute monthly debtors: {error}")
        raise
