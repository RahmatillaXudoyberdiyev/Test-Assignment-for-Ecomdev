import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.crud.student import (
    create_student,
    get_student_by_id,
    list_students,
    update_student,
    delete_student,
)
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate

logger = logging.getLogger("app.routers.students")
router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_new_student(
    student_in: StudentCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StudentRead:
    """Create a new student entry."""
    logger.info("HTTP POST /students requested: name='%s', group='%s'", student_in.name, student_in.group)
    try:
        student = await create_student(session=session, student_in=student_in)
        return student
    except Exception as error:
        logger.exception("HTTP POST /students failed: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not register student: {str(error)}",
        )


@router.get("", response_model=List[StudentRead])
async def get_all_students(
    skip: int = Query(0, ge=0, description="Offset records"),
    limit: int = Query(100, ge=1, le=500, description="Page limit"),
    group: Optional[str] = Query(None, description="Filter by group name"),
    session: AsyncSession = Depends(get_db_session),
) -> List[StudentRead]:
    """Retrieve students with optional group filtering and pagination."""
    logger.debug("HTTP GET /students requested: skip=%d, limit=%d, group=%s", skip, limit, group)
    try:
        students = await list_students(session=session, skip=skip, limit=limit, group=group)
        return students
    except Exception as error:
        logger.exception("HTTP GET /students failed: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch students: {str(error)}",
        )


@router.get("/{student_id}", response_model=StudentRead)
async def get_student(
    student_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> StudentRead:
    """Fetch details of a single student by ID."""
    logger.debug("HTTP GET /students/%d requested", student_id)
    try:
        student = await get_student_by_id(session=session, student_id=student_id)
        if not student:
            logger.warning("HTTP GET /students/%d: Student not found", student_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found",
            )
        return student
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("HTTP GET /students/%d encountered an error: %s", student_id, error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving student: {str(error)}",
        )


@router.put("/{student_id}", response_model=StudentRead)
async def update_existing_student(
    student_id: int,
    student_in: StudentUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> StudentRead:
    """Update student record details."""
    logger.info("HTTP PUT /students/%d requested", student_id)
    try:
        student = await get_student_by_id(session=session, student_id=student_id)
        if not student:
            logger.warning("HTTP PUT /students/%d: Student not found for update", student_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found",
            )
        updated = await update_student(session=session, student=student, student_in=student_in)
        return updated
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("HTTP PUT /students/%d failed: %s", student_id, error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update student: {str(error)}",
        )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_student(
    student_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete a student and all related payments."""
    logger.info("HTTP DELETE /students/%d requested", student_id)
    try:
        student = await get_student_by_id(session=session, student_id=student_id)
        if not student:
            logger.warning("HTTP DELETE /students/%d: Student not found for deletion", student_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found",
            )
        await delete_student(session=session, student=student)
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("HTTP DELETE /students/%d failed: %s", student_id, error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete student: {str(error)}",
        )
