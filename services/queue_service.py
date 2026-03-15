import math
from sqlalchemy import select
from database import SessionLocal
from models import Lab, Registration, User, AcademicStudent, Priority, Weight, Queue, QueueEntry, Subject
from config import K_FACTOR
from datetime import datetime

def calculate_new_weight(current_weight: float, position: int, total_n: int) -> float:
    if total_n <= 1:
        return current_weight
    mid = (total_n + 1) / 2.0
    delta = (position - mid) / total_n
    new_weight = current_weight * math.exp(K_FACTOR * delta)
    return max(0.1, min(new_weight, 10.0))

async def generate_queue_for_lab(lab_id: int, headman_user_id: int):
    async with SessionLocal() as session:
        lab = await session.get(Lab, lab_id)
        if not lab:
            raise ValueError("Лабораторная не найдена")
        if lab.is_closed:
            raise ValueError("Лабораторная закрыта")
        
        stmt = (
            select(Registration, User, AcademicStudent, Weight, Priority)
            .join(User, Registration.user_id == User.id)
            .join(AcademicStudent, User.academic_student_id == AcademicStudent.id)
            .outerjoin(Weight, (Weight.user_id == User.id) & (Weight.subject_id == lab.subject_id))
            .join(Priority, Registration.priority_id == Priority.id)
            .where(Registration.lab_id == lab_id)
        )
        result = await session.execute(stmt)
        registrations = result.all()
        
        if not registrations:
            raise ValueError("Нет зарегистрированных студентов")
        
        priorities_stmt = (
            select(Priority)
            .where(Priority.lab_id == lab_id)
            .order_by(Priority.priority_value.desc())
        )
        priorities = (await session.execute(priorities_stmt)).scalars().all()
        
        queue = Queue(lab_id=lab_id, created_at=datetime.utcnow())
        session.add(queue)
        await session.flush()
        
        global_position = 1
        affected_user_ids = set()
        
        for priority in priorities:
            group_regs = [r for r in registrations if r[4].id == priority.id]
            group_regs.sort(key=lambda x: x[3].value if x[3] else 1.0, reverse=True)
            total_in_group = len(group_regs)
            
            for rel_pos, (reg, user, student, weight_obj, prio) in enumerate(group_regs, 1):
                current_weight = weight_obj.value if weight_obj else 1.0
                
                if priority.affects_weight:
                    new_weight = calculate_new_weight(current_weight, rel_pos, total_in_group)
                else:
                    new_weight = current_weight
                
                entry = QueueEntry(
                    queue_id=queue.id,
                    user_id=user.id,
                    position=global_position,
                    priority_group=priority.priority_value,
                    weight_before=current_weight,
                    weight_after=new_weight
                )
                session.add(entry)
                
                if priority.affects_weight:
                    if weight_obj:
                        weight_obj.value = new_weight
                    else:
                        new_weight_obj = Weight(
                            group_id=lab.group_id,
                            user_id=user.id,
                            subject_id=lab.subject_id,
                            value=new_weight
                        )
                        session.add(new_weight_obj)
                    affected_user_ids.add(user.id)
                
                global_position += 1
        
        await session.commit()
        return queue
    
async def cascade_weight_recalculation(session, source_lab, affected_user_ids):
    stmt = (
        select(Lab)
        .where(
            Lab.subject_id == source_lab.subject_id,
            Lab.id != source_lab.id,
            Lab.date > source_lab.date,
            Lab.is_closed == False
        )
        .order_by(Lab.date.asc())
    )
    future_labs = (await session.execute(stmt)).scalars().all()
    for future_lab in future_labs:
        reg_stmt = (
            select(Registration, User, Weight, Priority)
            .join(User, Registration.user_id == User.id)
            .join(Priority, Registration.priority_id == Priority.id)
            .outerjoin(Weight, (Weight.user_id == User.id) & (Weight.subject_id == future_lab.subject_id))
            .where(Registration.lab_id == future_lab.id)
        )
        regs = (await session.execute(reg_stmt)).all()
        affected_in_lab = [r for r in regs if r[0].user_id in affected_user_ids]
        if not affected_in_lab:
            continue
        prio_stmt = (
            select(Priority)
            .where(Priority.lab_id == future_lab.id)
            .order_by(Priority.priority_value.desc())
        )
        priorities = (await session.execute(prio_stmt)).scalars().all()
        for priority in priorities:
            group_regs = [r for r in regs if r[3].id == priority.id]
            if not group_regs:
                continue
            group_regs.sort(key=lambda x: x[2].value if x[2] else 1.0, reverse=True)
            total_in_group = len(group_regs)
            for rel_pos, (reg, user, weight_obj, prio) in enumerate(group_regs, 1):
                if user.id not in affected_user_ids:
                    continue
                current_weight = weight_obj.value if weight_obj else 1.0
                if priority.affects_weight:
                    new_weight = await calculate_new_weight(current_weight, rel_pos, total_in_group)
                    if weight_obj:
                        weight_obj.value = new_weight
                    else:
                        new_weight_obj = Weight(
                            group_id=future_lab.group_id,
                            user_id=user.id,
                            subject_id=future_lab.subject_id,
                            value=new_weight
                        )
                        session.add(new_weight_obj)

async def get_queue_details(lab_id: int):
    async with SessionLocal() as session:
        queue = await session.execute(
            select(Queue).where(Queue.lab_id == lab_id)
        )
        queue = queue.scalar_one_or_none()
        if not queue:
            return None
        entries_stmt = (
            select(QueueEntry, User, AcademicStudent)
            .join(User, QueueEntry.user_id == User.id)
            .outerjoin(AcademicStudent, User.academic_student_id == AcademicStudent.id)
            .where(QueueEntry.queue_id == queue.id)
            .order_by(QueueEntry.position)
        )
        entries = (await session.execute(entries_stmt)).all()
        return {
            "entries": [
                {
                    "position": e[0].position,
                    "name": e[2].full_name if e[2] else e[1].username,
                    "weight": e[0].weight_after,
                    "priority_group": e[0].priority_group_value
                }
                for e in entries
            ]
        }

async def register_for_lab(lab_id: int, user_id: int, priority_id: int):
    async with SessionLocal() as session:
        existing = await session.execute(
            select(Registration).where(
                Registration.lab_id == lab_id,
                Registration.user_id == user_id
            )
        )
        existing = existing.scalar_one_or_none()
        if existing:
            existing.requested_priority_id = priority_id
            existing.is_priority_confirmed = False
            await session.commit()
            return existing
        registration = Registration(
            lab_id=lab_id,
            user_id=user_id,
            priority_id=priority_id,
            requested_priority_id=priority_id,
            is_priority_confirmed=False
        )
        session.add(registration)
        await session.commit()
        return registration

async def confirm_priority(registration_id: int, new_priority_id: int = None):
    async with SessionLocal() as session:
        reg = await session.get(Registration, registration_id)
        if not reg:
            raise ValueError("Регистрация не найдена")
        if new_priority_id:
            reg.priority_id = new_priority_id
        reg.is_priority_confirmed = True
        await session.commit()
        return reg

async def unregister_from_lab(lab_id: int, user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Registration).where(
                Registration.lab_id == lab_id,
                Registration.user_id == user_id
            )
        )
        reg = result.scalar_one_or_none()
        if reg:
            await session.delete(reg)
            await session.commit()
        return reg is not None