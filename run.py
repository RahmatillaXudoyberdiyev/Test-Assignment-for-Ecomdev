import asyncio
import sys
import uvicorn

from app.config import settings
from app.database import init_db
from app.main import app
from bot.main import create_bot_and_dispatcher


async def start_api_server() -> None:
    """Run uvicorn server within an asyncio task."""
    config = uvicorn.Config(
        app=app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    print(f"[Runner] FastAPI server running at http://{settings.API_HOST}:{settings.API_PORT}/api")
    await server.serve()


async def start_bot_service() -> None:
    """Run aiogram bot polling within an asyncio task."""
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_telegram_bot_token_here":
        print("[Runner Warning] BOT_TOKEN is missing or not set in .env. Bot polling will not start.")
        return

    bot, dp = create_bot_and_dispatcher()
    print("[Runner] Starting Telegram Bot polling...")
    try:
        await dp.start_polling(bot)
    except Exception as error:
        print(f"[Runner Error] Bot polling encountered an exception: {error}")
    finally:
        await bot.session.close()


async def main() -> None:
    """Initialize system and run services concurrently."""
    print("==================================================")
    print("  Education Center Payment-Tracking System")
    print("==================================================")
    await init_db()

    tasks = [asyncio.create_task(start_api_server())]
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "your_telegram_bot_token_here":
        tasks.append(asyncio.create_task(start_bot_service()))
    else:
        print("[Notice] Add your BOT_TOKEN to .env to run the Telegram Bot.")

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Runner] Shutdown requested by user. Exiting cleanly.")
        sys.exit(0)
