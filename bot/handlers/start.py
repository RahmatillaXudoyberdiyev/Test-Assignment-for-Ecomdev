from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.localization import get_text

router = Router(name="start_router")


@router.message(CommandStart())
async def handle_start_command(message: Message) -> None:
    """Handle /start command with localized introductory message."""
    user_id = message.from_user.id if message.from_user else None
    response_text = get_text("start_message", user_id=user_id)
    await message.answer(response_text, parse_mode="HTML")


@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    """Handle /help command explaining available functionality."""
    user_id = message.from_user.id if message.from_user else None
    response_text = get_text("help_message", user_id=user_id)
    await message.answer(response_text, parse_mode="HTML")
