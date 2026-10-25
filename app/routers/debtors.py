import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.crud.debtor import get_monthly_debtors
from app.schemas.debtor import DebtorRead

logger = logging.getLogger("app.routers.debtors")
router = APIRouter(prefix="/debtors", tags=["Debtors"])


@router.get("", response_model=List[DebtorRead])
async def get_debtors_list(
    month: Optional[str] = Query(
        None,
        description="Target month in YYYY-MM format (defaults to current month if omitted)",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    ),
    session: AsyncSession = Depends(get_db_session),
) -> List[DebtorRead]:
    """Retrieve students with outstanding debts for a specified month."""
    logger.info("HTTP GET /debtors requested for month='%s'", month)
    try:
        debtors = await get_monthly_debtors(session=session, month_str=month)
        return debtors
    except Exception as error:
        logger.exception("HTTP GET /debtors failed for month='%s': %s", month, error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not compute debtors list: {str(error)}",
        )
