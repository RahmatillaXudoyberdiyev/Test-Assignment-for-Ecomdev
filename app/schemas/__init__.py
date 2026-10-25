from app.schemas.student import StudentBase, StudentCreate, StudentUpdate, StudentRead
from app.schemas.payment import PaymentBase, PaymentCreate, PaymentRead
from app.schemas.debtor import DebtorRead

__all__ = [
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentRead",
    "PaymentBase",
    "PaymentCreate",
    "PaymentRead",
    "DebtorRead",
]
