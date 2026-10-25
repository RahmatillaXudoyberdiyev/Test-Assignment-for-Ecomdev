import logging
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.localization import get_text

logger = logging.getLogger("bot.handlers.start")
router = Router(name="start_router")


@router.message(CommandStart())
async def handle_start_command(message: Message) -> None:
    """Handle /start command with localized introductory message."""
    user_id = message.from_user.id if message.from_user else None
    username = message.from_user.username if message.from_user else "unknown"
    logger.info("Received /start from user_id=%s (@%s)", user_id, username)

    try:
        response_text = get_text("start_message", user_id=user_id)
        await message.answer(response_text, parse_mode="HTML")
        logger.debug("Sent /start response to user_id=%s", user_id)
    except Exception as error:
        logger.exception("Failed to reply to /start for user_id=%s: %s", user_id, error)


@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    """Handle /help command explaining available functionality."""
    user_id = message.from_user.id if message.from_user else None
    username = message.from_user.username if message.from_user else "unknown"
    logger.info("Received /help from user_id=%s (@%s)", user_id, username)

    try:
        response_text = get_text("help_message", user_id=user_id)
        await message.answer(response_text, parse_mode="HTML")
        logger.debug("Sent /help response to user_id=%s", user_id)
    except Exception as error:
        logger.exception("Failed to reply to /help for user_id=%s: %s", user_id, error)
