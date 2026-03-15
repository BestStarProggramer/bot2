from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from services.lab_service import create_lab, get_group_labs, get_lab_details, is_registered_for_lab, get_lab_priorities
from services.permission_service import can_manage_queue
from services.queue_service import register_for_lab, unregister_from_lab
from keyboards.lab_keyboards import get_labs_keyboard, get_lab_details_keyboard, get_lab_admin_keyboard, get_priority_selection_keyboard

router = Router()

class LabState(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
    subject_id = State()
    group_id = State()

async def show_labs_for_group(callback: CallbackQuery, group_id: int):
    labs = await get_group_labs(group_id)
    if not labs:
        await callback.message.answer("📅 Нет запланированных лабораторных")
        await callback.answer()
        return
    await callback.message.answer("📅 Календарь лабораторных:", reply_markup=get_labs_keyboard(labs))
    await callback.answer()

@router.callback_query(F.data.startswith("create_lab_"))
async def create_lab_start(callback: CallbackQuery):
    group_id = int(callback.data.replace("create_lab_", ""))
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == callback.from_user.id
            )
        )
        member = result.scalar_one_or_none()
    if not member or not can_manage_queue(member):
        await callback.answer("Нет прав", show_alert=True)
        return
    from services.subject_service import get_group_subjects
    subjects = await get_group_subjects(group_id)
    if not subjects:
        await callback.answer("Сначала добавьте предметы в группу", show_alert=True)
        return
    buttons = []
    for subject in subjects:
        buttons.append([InlineKeyboardButton(text=subject.name, callback_data=f"lab_subject_{subject.id}_{group_id}")])
    await callback.message.answer("Выберите предмет для лабораторной:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("lab_subject_"))
async def lab_subject_selected(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.replace("lab_subject_", "").split("_")
    subject_id = int(parts[0])
    group_id = int(parts[1])
    await state.update_data(subject_id=subject_id, group_id=group_id)
    await state.set_state(LabState.waiting_for_date)
    await callback.message.answer("Введите дату (ДД.ММ.ГГГГ):")
    await callback.answer()

@router.message(F.text, LabState.waiting_for_date)
async def lab_date_handler(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        await state.update_data(date=date)
        await state.set_state(LabState.waiting_for_time)
        await message.answer("Введите время (ЧЧ:ММ):")
    except ValueError:
        await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

@router.message(F.text, LabState.waiting_for_time)
async def lab_time_handler(message: Message, state: FSMContext):
    try:
        time = datetime.strptime(message.text.strip(), "%H:%M").time()
        data = await state.get_data()
        subject_id = data.get("subject_id")
        group_id = data.get("group_id")
        date = data.get("date")
        if not all([subject_id, group_id, date]):
            await message.answer("Ошибка: данные сессии утеряны. Начните заново.")
            await state.clear()
            return
        lab_datetime = datetime.combine(date.date(), time)
        lab = await create_lab(group_id, subject_id, lab_datetime)
        await message.answer(f"✅ Лабораторная создана!\nПредмет ID: {subject_id}\nДата: {lab_datetime.strftime('%d.%m.%Y %H:%M')}")
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат времени. Используйте ЧЧ:ММ")

@router.callback_query(F.data.startswith("lab_"))
async def lab_details_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("lab_", ""))
    lab = await get_lab_details(lab_id)
    if not lab:
        await callback.answer("Лабораторная не найдена", show_alert=True)
        return
    
    is_registered = await is_registered_for_lab(lab_id, callback.from_user.id)
    
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == lab["group_id"],
                GroupMember.user_id == callback.from_user.id
            )
        )
        member = result.scalar_one_or_none()
    can_manage = member and can_manage_queue(member)
    
    await callback.message.answer(
        f"📚 {lab['subject']} — {lab['date'].strftime('%d.%m %H:%M')}",
        reply_markup=get_lab_details_keyboard(lab_id, is_registered, lab['is_closed'], can_manage)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("join_lab_"))
async def join_lab_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("join_lab_", ""))
    priorities = await get_lab_priorities(lab_id)
    if not priorities:
        await callback.answer("Нет доступных приоритетов", show_alert=True)
        return
    await callback.message.answer("Выберите приоритет:", reply_markup=get_priority_selection_keyboard(priorities, lab_id))
    await callback.answer()

@router.callback_query(F.data.startswith("select_priority_"))
async def select_priority_handler(callback: CallbackQuery):
    parts = callback.data.replace("select_priority_", "").split("_")
    priority_id = int(parts[0])
    lab_id = int(parts[1])
    await register_for_lab(lab_id, callback.from_user.id, priority_id)
    await callback.message.answer("✅ Вы записаны на лабораторную!")
    await callback.answer()

@router.callback_query(F.data.startswith("leave_lab_"))
async def leave_lab_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("leave_lab_", ""))
    await unregister_from_lab(lab_id, callback.from_user.id)
    await callback.message.answer("❌ Вы покинули очередь")
    await callback.answer()

@router.callback_query(F.data.startswith("admin_lab_"))
async def admin_lab_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("admin_lab_", ""))
    lab = await get_lab_details(lab_id)
    if not lab:
        await callback.answer("Лабораторная не найдена", show_alert=True)
        return
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == lab["group_id"],
                GroupMember.user_id == callback.from_user.id
            )
        )
        member = result.scalar_one_or_none()
    if not member or not can_manage_queue(member):
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.message.answer("Управление лабораторной:", reply_markup=get_lab_admin_keyboard(lab_id, lab["group_id"]))
    await callback.answer()

@router.callback_query(F.data.startswith("swap_lab_"))
async def swap_lab_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("swap_lab_", ""))
    from services.swap_service import get_lab_students_for_swap
    students = await get_lab_students_for_swap(lab_id, callback.from_user.id)
    if not students:
        await callback.answer("Нет доступных студентов для обмена", show_alert=True)
        return
    from keyboards.swap_keyboards import get_swap_keyboard
    await callback.message.answer("Выберите студента для обмена:", reply_markup=get_swap_keyboard(lab_id, students, callback.from_user.id))
    await callback.answer()