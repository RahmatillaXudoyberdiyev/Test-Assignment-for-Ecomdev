from bot.handlers.start import router as start_router
from bot.handlers.debt import router as debt_router
from bot.handlers.pay import router as pay_router

__all__ = ["start_router", "debt_router", "pay_router"]
