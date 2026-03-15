from sqlalchemy import select
from database import SessionLocal
from models import Subject

async def add_subject(group_id: int, name: str):
    async with SessionLocal() as session:
        subject = Subject(group_id=group_id, name=name)
        session.add(subject)
        await session.commit()
        await session.refresh(subject)
        return subject

async def get_group_subjects(group_id: int):
    async with SessionLocal() as session:
        result = await session.execute(select(Subject).where(Subject.group_id == group_id))
        return result.scalars().all()

async def get_subject_by_id(subject_id: int):
    async with SessionLocal() as session:
        return await session.get(Subject, subject_id)

async def delete_subject(subject_id: int):
    async with SessionLocal() as session:
        subject = await session.get(Subject, subject_id)
        if subject:
            await session.delete(subject)
            await session.commit()