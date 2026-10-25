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

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_new_student(
    student_in: StudentCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StudentRead:
    """Create a new student entry."""
    try:
        student = await create_student(session=session, student_in=student_in)
        return student
    except Exception as error:
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
    try:
        return await list_students(session=session, skip=skip, limit=limit, group=group)
    except Exception as error:
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
    student = await get_student_by_id(session=session, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    return student


@router.put("/{student_id}", response_model=StudentRead)
async def update_existing_student(
    student_id: int,
    student_in: StudentUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> StudentRead:
    """Update student record details."""
    student = await get_student_by_id(session=session, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    try:
        updated = await update_student(session=session, student=student, student_in=student_in)
        return updated
    except Exception as error:
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
    student = await get_student_by_id(session=session, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    try:
        await delete_student(session=session, student=student)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete student: {str(error)}",
        )
