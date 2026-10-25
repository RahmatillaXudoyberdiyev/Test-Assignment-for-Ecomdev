import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.models.payment import Payment
from app.schemas.debtor import DebtorRead

logger = logging.getLogger("app.crud.debtor")


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
                raise ValueError("Expected format YYYY-MM")
            year = int(parts[0])
            month = int(parts[1])
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")
            month_label = f"{year:04d}-{month:02d}"
        except Exception as error:
            logger.warning("Invalid month string '%s', falling back to current month: %s", month_str, error)
            year = now.year
            month = now.month
            month_label = f"{year:04d}-{month:02d}"

    start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    logger.debug("Computed month range for '%s': start=%s, end=%s", month_label, start_date, end_date)
    return start_date, end_date, month_label


async def get_monthly_debtors(
    session: AsyncSession,
    month_str: Optional[str] = None,
) -> List[DebtorRead]:
    """Retrieve students who paid less than their agreed monthly fee for the given month."""
    try:
        start_date, end_date, month_label = parse_target_month_range(month_str)
        logger.info("Computing monthly debtors for period: %s", month_label)

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

        logger.info("Debtor calculation finished: %d debtors found for %s out of %d students evaluated.", len(debtors), month_label, len(rows))
        return debtors
    except Exception as error:
        logger.exception("Failed to calculate monthly debtors for '%s': %s", month_str, error)
        raise
