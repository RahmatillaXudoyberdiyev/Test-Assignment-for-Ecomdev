import asyncio
import logging
from aiogram import Bot, Dispatcher

from app.config import settings
from app.database import init_db
from app.logger import setup_logging
from bot.handlers import start_router, debt_router, pay_router

setup_logging()
logger = logging.getLogger("bot.main")


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Create and configure the aiogram Bot and Dispatcher instances."""
    logger.debug("Creating Bot and Dispatcher instances...")
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(debt_router)
    dp.include_router(pay_router)
    logger.debug("Routers registered successfully in Dispatcher.")

    return bot, dp


async def run_bot() -> None:
    """Start Telegram bot polling service."""
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_telegram_bot_token_here":
        logger.warning("BOT_TOKEN is not configured in .env. Bot polling skipped.")
        return

    logger.info("Initializing database for bot service...")
    try:
        await init_db()
    except Exception as error:
        logger.exception("Failed to initialize database during bot startup: %s", error)
        raise

    bot, dp = create_bot_and_dispatcher()
    logger.info("Bot polling starting up...")
    try:
        await dp.start_polling(bot)
    except Exception as error:
        logger.exception("Bot polling stopped due to error: %s", error)
    finally:
        await bot.session.close()
        logger.info("Bot session closed cleanly.")


if __name__ == "__main__":
    asyncio.run(run_bot())
