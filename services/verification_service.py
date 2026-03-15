from sqlalchemy import select
from database import SessionLocal
from models import AcademicStudent, User, GroupMember, Group
from config import ADMINS

async def add_student_to_group(group_id: int, full_name: str):
    async with SessionLocal() as session:
        student = AcademicStudent(group_id=group_id, full_name=full_name)
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student

async def get_group_students(group_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(AcademicStudent)
            .where(AcademicStudent.group_id == group_id, AcademicStudent.is_active == True)
        )
        return result.scalars().all()

async def claim_student(student_id: int, user_id: int):
    async with SessionLocal() as session:
        student = await session.get(AcademicStudent, student_id)
        if not student:
            raise ValueError("Студент не найден")
        if student.user_id is not None:
            raise ValueError("Этот студент уже привязан к другому пользователю")
        student.user_id = user_id
        await session.commit()
        return student

async def verify_student(user_id: int, student_id: int, approved: bool):
    async with SessionLocal() as session:
        student = await session.get(AcademicStudent, student_id)
        if not student:
            raise ValueError("Студент не найден")
        if approved:
            user = await session.get(User, user_id)
            if user:
                user.academic_student_id = student_id
                user.is_verified = True
        else:
            student.user_id = None
        await session.commit()

async def get_pending_claims(group_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(AcademicStudent, User)
            .join(User, AcademicStudent.user_id == User.id)
            .where(
                AcademicStudent.group_id == group_id,
                AcademicStudent.user_id.isnot(None),
                User.is_verified == False
            )
        )
        return result.all()

async def get_user_student(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(AcademicStudent).where(AcademicStudent.user_id == user_id)
        )
        return result.scalar_one_or_none()