import asyncio
import logging
import sys
import uvicorn

from app.config import settings
from app.database import init_db
from app.logger import setup_logging
from app.main import app
from bot.main import create_bot_and_dispatcher

setup_logging()
logger = logging.getLogger("run")


async def start_api_server() -> None:
    """Run uvicorn server within an asyncio task."""
    logger.info("Preparing FastAPI server on %s:%d...", settings.API_HOST, settings.API_PORT)
    config = uvicorn.Config(
        app=app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    logger.info("FastAPI documentation available at http://%s:%d/api", settings.API_HOST, settings.API_PORT)
    try:
        await server.serve()
    except Exception as error:
        logger.exception("FastAPI server encountered an error: %s", error)
        raise


async def start_bot_service() -> None:
    """Run aiogram bot polling within an asyncio task."""
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_telegram_bot_token_here":
        logger.warning("BOT_TOKEN is missing or not set in .env. Bot polling will not start.")
        return

    logger.info("Initializing Telegram Bot dispatcher...")
    bot, dp = create_bot_and_dispatcher()
    logger.info("Starting Telegram Bot polling loop...")
    try:
        await dp.start_polling(bot)
    except Exception as error:
        logger.exception("Bot polling encountered an exception: %s", error)
    finally:
        await bot.session.close()
        logger.info("Bot session finalized.")


async def main() -> None:
    """Initialize system and run services concurrently."""
    logger.info("==================================================")
    logger.info("  Education Center Payment-Tracking System")
    logger.info("==================================================")

    try:
        await init_db()
    except Exception as error:
        logger.exception("Critical error during database initialization: %s", error)
        sys.exit(1)

    tasks = [asyncio.create_task(start_api_server())]
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "your_telegram_bot_token_here":
        tasks.append(asyncio.create_task(start_bot_service()))
    else:
        logger.info("Notice: Add your live BOT_TOKEN to .env to run the Telegram Bot.")

    try:
        await asyncio.gather(*tasks)
    except Exception as error:
        logger.exception("Task runner error: %s", error)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user. Exiting cleanly.")
        sys.exit(0)
