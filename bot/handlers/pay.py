import logging
from datetime import datetime, timezone
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from app.database import async_session_factory
from app.crud.student import get_student_by_id
from app.crud.payment import create_payment
from app.crud.debtor import parse_target_month_range
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate
from bot.localization import get_text

logger = logging.getLogger("bot.handlers.pay")
router = Router(name="pay_router")


@router.message(Command("pay"))
async def handle_pay_command(message: Message) -> None:
    """Handle /pay <student_id> <amount> command."""
    user_id = message.from_user.id if message.from_user else None
    username = message.from_user.username if message.from_user else "unknown"
    raw_command = (message.text or "").strip()
    logger.info("Received /pay from user_id=%s (@%s): '%s'", user_id, username, raw_command)

    parts = raw_command.split()
    if len(parts) < 3:
        logger.warning("Invalid /pay syntax from user_id=%s: parts=%s", user_id, parts)
        usage = get_text("pay_usage", user_id=user_id)
        await message.answer(usage, parse_mode="HTML")
        return

    raw_id = parts[1]
    raw_amount = parts[2]

    try:
        student_id = int(raw_id)
        amount = float(raw_amount.replace(",", "."))
    except ValueError as parse_err:
        logger.warning("Failed parsing /pay parameters ('%s', '%s') from user_id=%s: %s", raw_id, raw_amount, user_id, parse_err)
        err = get_text("pay_invalid_types", user_id=user_id)
        await message.answer(err, parse_mode="HTML")
        return

    if student_id <= 0 or amount <= 0:
        logger.warning("Non-positive /pay values from user_id=%s: student_id=%d, amount=%.2f", user_id, student_id, amount)
        err = get_text("pay_amount_positive", user_id=user_id)
        await message.answer(err, parse_mode="HTML")
        return

    try:
        async with async_session_factory() as session:
            logger.debug("Verifying student existence: student_id=%d", student_id)
            student = await get_student_by_id(session=session, student_id=student_id)
            if not student:
                logger.warning("Student id=%d does not exist. Rejecting payment from user_id=%s", student_id, user_id)
                not_found = get_text("student_not_found", user_id=user_id, student_id=student_id)
                await message.answer(not_found, parse_mode="HTML")
                return

            logger.info("Recording payment of %.2f for student id=%d (%s)", amount, student.id, student.name)
            payment_in = PaymentCreate(student_id=student_id, amount=amount)
            new_payment = await create_payment(session=session, payment_in=payment_in)

            start_date, end_date, month_label = parse_target_month_range()
            start_naive = start_date.replace(tzinfo=None)
            end_naive = end_date.replace(tzinfo=None)

            sum_stmt = select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                Payment.student_id == student_id,
                (
                    ((Payment.date >= start_date) & (Payment.date < end_date))
                    | ((Payment.date >= start_naive) & (Payment.date < end_naive))
                ),
            )
            sum_result = await session.execute(sum_stmt)
            total_paid = float(sum_result.scalar_one_or_none() or 0.0)

            monthly_due = float(student.monthly_payment_amount)
            balance = monthly_due - total_paid

            if balance <= 0:
                if balance == 0:
                    status_balance = get_text("balance_fully_paid", user_id=user_id)
                else:
                    status_balance = get_text(
                        "balance_overpaid",
                        user_id=user_id,
                        overpaid=f"{abs(balance):,.2f}",
                    )
            else:
                status_balance = get_text(
                    "balance_debt_remaining",
                    user_id=user_id,
                    remaining=f"{balance:,.2f}",
                )

            date_str = new_payment.date.strftime("%Y-%m-%d %H:%M:%S")
            success_msg = get_text(
                "payment_success",
                user_id=user_id,
                name=student.name,
                student_id=student.id,
                group=student.group,
                amount=f"{amount:,.2f}",
                date=date_str,
                month=month_label,
                total_paid=f"{total_paid:,.2f}",
                monthly_payment_amount=f"{monthly_due:,.2f}",
                status_balance=status_balance,
            )
            await message.answer(success_msg, parse_mode="HTML")
            logger.info("Successfully recorded payment id=%d and replied to user_id=%s", new_payment.id, user_id)
    except Exception as error:
        logger.exception("Failed processing /pay for user_id=%s: %s", user_id, error)
        try:
            err_msg = get_text("system_error", user_id=user_id)
            await message.answer(err_msg, parse_mode="HTML")
        except Exception as reply_err:
            logger.exception("Failed to send error notification to user_id=%s: %s", user_id, reply_err)
