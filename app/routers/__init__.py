from app.routers.students import router as students_router
from app.routers.payments import router as payments_router
from app.routers.debtors import router as debtors_router

__all__ = ["students_router", "payments_router", "debtors_router"]
