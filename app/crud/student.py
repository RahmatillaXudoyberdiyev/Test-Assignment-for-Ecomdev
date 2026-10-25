from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


async def create_student(session: AsyncSession, student_in: StudentCreate) -> Student:
    """Create and persist a new student record in the database."""
    try:
        student = Student(
            name=student_in.name,
            phone_number=student_in.phone_number,
            group=student_in.group,
            monthly_payment_amount=student_in.monthly_payment_amount,
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        print(f"[CRUD] Created student: id={student.id}, name={student.name}")
        return student
    except Exception as error:
        await session.rollback()
        print(f"[CRUD Error] Failed to create student: {error}")
        raise


async def get_student_by_id(session: AsyncSession, student_id: int) -> Optional[Student]:
    """Retrieve a single student by primary key identifier."""
    try:
        statement = select(Student).where(Student.id == student_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    except Exception as error:
        print(f"[CRUD Error] Failed to fetch student id={student_id}: {error}")
        raise


async def list_students(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    group: Optional[str] = None,
) -> List[Student]:
    """Retrieve a list of students with optional filtering and pagination."""
    try:
        statement = select(Student)
        if group:
            statement = statement.where(Student.group == group)
        statement = statement.offset(skip).limit(limit).order_by(Student.id.asc())
        result = await session.execute(statement)
        return list(result.scalars().all())
    except Exception as error:
        print(f"[CRUD Error] Failed to list students: {error}")
        raise


async def update_student(
    session: AsyncSession,
    student: Student,
    student_in: StudentUpdate,
) -> Student:
    """Update existing student attributes with provided non-empty values."""
    try:
        update_data = student_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        await session.commit()
        await session.refresh(student)
        print(f"[CRUD] Updated student id={student.id}")
        return student
    except Exception as error:
        await session.rollback()
        print(f"[CRUD Error] Failed to update student id={student.id}: {error}")
        raise


async def delete_student(session: AsyncSession, student: Student) -> bool:
    """Delete a student and cascade delete associated payments."""
    try:
        student_id = student.id
        await session.delete(student)
        await session.commit()
        print(f"[CRUD] Deleted student id={student_id}")
        return True
    except Exception as error:
        await session.rollback()
        print(f"[CRUD Error] Failed to delete student id={student.id}: {error}")
        raise
