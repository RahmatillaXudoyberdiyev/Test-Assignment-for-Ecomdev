from datetime import datetime, timezone
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database import async_session_factory
from app.crud.debtor import get_monthly_debtors
from bot.localization import get_text

router = Router(name="debt_router")


@router.message(Command("debt"))
async def handle_debt_command(message: Message) -> None:
    """Handle /debt command listing debtors for the current month."""
    user_id = message.from_user.id if message.from_user else None
    current_month_str = datetime.now(timezone.utc).strftime("%Y-%m")

    try:
        async with async_session_factory() as session:
            debtors = await get_monthly_debtors(session=session, month_str=current_month_str)

        if not debtors:
            text = get_text("no_debtors", user_id=user_id, month=current_month_str)
            await message.answer(text, parse_mode="HTML")
            return

        header = get_text("debtors_header", user_id=user_id, month=current_month_str)
        items = []
        total_debt = 0.0

        for idx, debtor in enumerate(debtors, start=1):
            total_debt += debtor.debt
            item_text = get_text(
                "debtor_item",
                user_id=user_id,
                index=idx,
                name=debtor.name,
                group=debtor.group,
                student_id=debtor.student_id,
                debt=f"{debtor.debt:,.2f}",
                total_paid=f"{debtor.total_paid:,.2f}",
                monthly_payment_amount=f"{debtor.monthly_payment_amount:,.2f}",
                phone_number=debtor.phone_number,
            )
            items.append(item_text)

        footer = get_text(
            "debtors_footer",
            user_id=user_id,
            count=len(debtors),
            total_debt=f"{total_debt:,.2f}",
        )

        full_message = header + "".join(items) + footer
        await message.answer(full_message, parse_mode="HTML")
    except Exception as error:
        print(f"[Bot Error] /debt handling failed: {error}")
        err_msg = get_text("system_error", user_id=user_id)
        await message.answer(err_msg, parse_mode="HTML")
