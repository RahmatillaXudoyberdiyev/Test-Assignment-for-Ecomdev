import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate

logger = logging.getLogger("app.crud.student")


async def create_student(session: AsyncSession, student_in: StudentCreate) -> Student:
    """Create and persist a new student record in the database."""
    try:
        logger.info("Creating student: name='%s', group='%s', fee=%s", student_in.name, student_in.group, student_in.monthly_payment_amount)
        student = Student(
            name=student_in.name,
            phone_number=student_in.phone_number,
            group=student_in.group,
            monthly_payment_amount=student_in.monthly_payment_amount,
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        logger.info("Successfully created student: id=%d, name='%s'", student.id, student.name)
        return student
    except Exception as error:
        await session.rollback()
        logger.exception("Failed to create student '%s': %s", student_in.name, error)
        raise


async def get_student_by_id(session: AsyncSession, student_id: int) -> Optional[Student]:
    """Retrieve a single student by primary key identifier."""
    try:
        logger.debug("Fetching student with id=%d", student_id)
        statement = select(Student).where(Student.id == student_id)
        result = await session.execute(statement)
        student = result.scalar_one_or_none()
        if student:
            logger.debug("Found student id=%d: name='%s'", student_id, student.name)
        else:
            logger.debug("Student with id=%d was not found.", student_id)
        return student
    except Exception as error:
        logger.exception("Failed to fetch student id=%d: %s", student_id, error)
        raise


async def list_students(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    group: Optional[str] = None,
) -> List[Student]:
    """Retrieve a list of students with optional filtering and pagination."""
    try:
        logger.debug("Listing students: skip=%d, limit=%d, group=%s", skip, limit, group)
        statement = select(Student)
        if group:
            statement = statement.where(Student.group == group)
        statement = statement.offset(skip).limit(limit).order_by(Student.id.asc())
        result = await session.execute(statement)
        students = list(result.scalars().all())
        logger.debug("Retrieved %d students.", len(students))
        return students
    except Exception as error:
        logger.exception("Failed to list students: %s", error)
        raise


async def update_student(
    session: AsyncSession,
    student: Student,
    student_in: StudentUpdate,
) -> Student:
    """Update existing student attributes with provided non-empty values."""
    try:
        logger.info("Updating student id=%d", student.id)
        update_data = student_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        await session.commit()
        await session.refresh(student)
        logger.info("Successfully updated student id=%d with fields: %s", student.id, list(update_data.keys()))
        return student
    except Exception as error:
        await session.rollback()
        logger.exception("Failed to update student id=%d: %s", student.id, error)
        raise


async def delete_student(session: AsyncSession, student: Student) -> bool:
    """Delete a student and cascade delete associated payments."""
    try:
        student_id = student.id
        logger.info("Deleting student id=%d (name='%s')", student_id, student.name)
        await session.delete(student)
        await session.commit()
        logger.info("Successfully deleted student id=%d", student_id)
        return True
    except Exception as error:
        await session.rollback()
        logger.exception("Failed to delete student id=%d: %s", student.id, error)
        raise
