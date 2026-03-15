from sqlalchemy import select
from database import SessionLocal
from models import Lab, Subject, Registration, Priority
from datetime import datetime

async def create_lab(group_id: int, subject_id: int, date: datetime):
    async with SessionLocal() as session:
        lab = Lab(group_id=group_id, subject_id=subject_id, date=date)
        session.add(lab)
        await session.commit()
        await session.refresh(lab)
        default_priority = Priority(lab_id=lab.id, name="Обычный", emoji="😭", priority_value=0, affects_weight=False)
        session.add(default_priority)
        await session.commit()
        return lab

async def get_group_labs(group_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Lab).where(Lab.group_id == group_id, Lab.is_closed == False).order_by(Lab.date)
        )
        return result.scalars().all()

async def get_lab_details(lab_id: int):
    async with SessionLocal() as session:
        lab = await session.get(Lab, lab_id)
        if not lab:
            return None
        subject = await session.get(Subject, lab.subject_id)
        return {
            "id": lab.id,
            "subject": subject.name if subject else "Unknown",
            "subject_id": lab.subject_id,
            "date": lab.date,
            "is_closed": lab.is_closed,
            "group_id": lab.group_id
        }

async def close_lab(lab_id: int):
    async with SessionLocal() as session:
        lab = await session.get(Lab, lab_id)
        if lab:
            lab.is_closed = True
            await session.commit()
        return lab

async def is_registered_for_lab(lab_id: int, user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Registration).where(
                Registration.lab_id == lab_id,
                Registration.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

async def get_lab_priorities(lab_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Priority).where(Priority.lab_id == lab_id).order_by(Priority.priority_value.desc())
        )
        return result.scalars().all()

async def add_lab_priority(lab_id: int, name: str, emoji: str, priority_value: int, affects_weight: bool = True):
    async with SessionLocal() as session:
        priority = Priority(
            lab_id=lab_id,
            name=name,
            emoji=emoji,
            priority_value=priority_value,
            affects_weight=affects_weight
        )
        session.add(priority)
        await session.commit()
        await session.refresh(priority)
        return priority

async def get_lab_registrations(lab_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Registration).where(Registration.lab_id == lab_id)
        )
        return result.scalars().all()