from sqlalchemy import select
from database import SessionLocal
from models import SwapRequest, Registration, Lab, QueueEntry, Priority, User, AcademicStudent
from services.queue_service import calculate_new_weight, cascade_weight_recalculation

async def create_swap_request(lab_id: int, from_user_id: int, to_user_id: int):
    async with SessionLocal() as session:
        reg_stmt = (
            select(Registration, Priority)
            .join(Priority, Registration.priority_id == Priority.id)
            .where(Registration.lab_id == lab_id)
        )
        regs = {r[0].user_id: (r[0], r[1]) for r in (await session.execute(reg_stmt)).all()}
        if from_user_id not in regs or to_user_id not in regs:
            raise ValueError("Один из пользователей не записан на эту лабу")
        from_prio = regs[from_user_id][1].priority_value
        to_prio = regs[to_user_id][1].priority_value
        if from_prio != to_prio:
            raise ValueError("Обмен возможен только внутри одной приоритетной группы")
        lab = await session.get(Lab, lab_id)
        if lab.is_closed:
            raise ValueError("Лабораторная закрыта")
        from_pos = next((i for i, r in enumerate(regs.keys()) if r == from_user_id), 0)
        to_pos = next((i for i, r in enumerate(regs.keys()) if r == to_user_id), 0)
        swap = SwapRequest(
            lab_id=lab_id,
            from_user=from_user_id,
            to_user=to_user_id,
            from_position=from_pos + 1,
            to_position=to_pos + 1,
            status="pending"
        )
        session.add(swap)
        await session.commit()
        await session.refresh(swap)
        return swap

async def accept_swap_request(swap_id: int, accepter_user_id: int):
    async with SessionLocal() as session:
        swap = await session.get(SwapRequest, swap_id)
        if not swap:
            raise ValueError("Заявка не найдена")
        if swap.status != "pending":
            raise ValueError("Заявка уже обработана")
        if swap.to_user != accepter_user_id:
            raise ValueError("Это не ваша заявка")
        lab = await session.get(Lab, swap.lab_id)
        if lab.is_closed:
            swap.status = "cancelled"
            await session.commit()
            raise ValueError("Лабораторная уже закрыта")
        swap.status = "accepted"
        await session.commit()
        return swap

async def reject_swap_request(swap_id: int, user_id: int):
    async with SessionLocal() as session:
        swap = await session.get(SwapRequest, swap_id)
        if not swap:
            raise ValueError("Заявка не найдена")
        if swap.to_user != user_id:
            raise ValueError("Это не ваша заявка")
        swap.status = "rejected"
        await session.commit()
        return swap

async def get_pending_swaps(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(SwapRequest)
            .where(SwapRequest.to_user == user_id, SwapRequest.status == "pending")
        )
        return result.scalars().all()

async def get_swap_details(swap_id: int):
    async with SessionLocal() as session:
        swap = await session.get(SwapRequest, swap_id)
        if not swap:
            return None
        from_user = await session.get(User, swap.from_user)
        to_user = await session.get(User, swap.to_user)
        lab = await session.get(Lab, swap.lab_id)
        from_student = await session.execute(
            select(AcademicStudent).where(AcademicStudent.user_id == swap.from_user)
        )
        from_student = from_student.scalar_one_or_none()
        return {
            "swap": swap,
            "from_name": from_student.full_name if from_student else from_user.username if from_user else "Unknown",
            "to_name": to_user.username if to_user else "Unknown",
            "lab_subject": lab.subject.name if lab and lab.subject else "Unknown",
            "lab_date": lab.date if lab else None
        }

async def get_lab_students_for_swap(lab_id: int, current_user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Registration, User, AcademicStudent, Priority)
            .join(User, Registration.user_id == User.id)
            .outerjoin(AcademicStudent, User.academic_student_id == AcademicStudent.id)
            .join(Priority, Registration.priority_id == Priority.id)
            .where(Registration.lab_id == lab_id)
        )
        all_regs = result.all()
        current_prio = None
        for reg, user, student, prio in all_regs:
            if reg.user_id == current_user_id:
                current_prio = prio.priority_value
                break
        if current_prio is None:
            return []
        students = []
        for reg, user, student, prio in all_regs:
            if reg.user_id != current_user_id and prio.priority_value == current_prio:
                students.append({
                    "user_id": user.id,
                    "name": student.full_name if student else user.username,
                    "priority_value": prio.priority_value
                })
        return students