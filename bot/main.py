import asyncio
from aiogram import Bot, Dispatcher

from app.config import settings
from app.database import init_db
from bot.handlers import start_router, debt_router, pay_router


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Create and configure the aiogram Bot and Dispatcher instances."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(debt_router)
    dp.include_router(pay_router)

    return bot, dp


async def run_bot() -> None:
    """Start Telegram bot polling service."""
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_telegram_bot_token_here":
        print("[Bot Warning] BOT_TOKEN is not configured in .env. Bot polling skipped.")
        return

    print("[Bot] Initializing database for bot service...")
    await init_db()

    bot, dp = create_bot_and_dispatcher()
    print("[Bot] Bot polling started successfully.")
    try:
        await dp.start_polling(bot)
    except Exception as error:
        print(f"[Bot Error] Polling stopped due to error: {error}")
    finally:
        await bot.session.close()
        print("[Bot] Bot session closed.")


if __name__ == "__main__":
    asyncio.run(run_bot())
