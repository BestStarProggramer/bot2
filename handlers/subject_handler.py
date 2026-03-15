from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.subject_service import add_subject, get_group_subjects, get_subject_by_id
from services.permission_service import can_manage_queue
from keyboards.subject_keyboards import get_subjects_keyboard, get_subject_actions_keyboard

router = Router()

class SubjectNameState(StatesGroup):
    waiting_for_name = State()
    selecting_group = State()

async def show_subjects_for_group(callback: CallbackQuery, group_id: int):
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(GroupMember.user_id == callback.from_user.id)
        )
        member = result.scalar_one_or_none()
    if not member or not can_manage_queue(member):
        await callback.answer("Нет прав для просмотра предметов", show_alert=True)
        return
    subjects = await get_group_subjects(group_id)
    if not subjects:
        await callback.message.answer("Нет предметов в этой группе")
        await callback.answer()
        return
    await callback.message.answer("Предметы группы:", reply_markup=get_subjects_keyboard(subjects, group_id))
    await callback.answer()

@router.callback_query(F.data == "add_subject")
async def add_subject_start(callback: CallbackQuery):
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id))
        members = result.scalars().all()
    if not members:
        await callback.answer("Вы не состоите ни в одной группе", show_alert=True)
        return
    admin_members = [m for m in members if can_manage_queue(m)]
    if not admin_members:
        await callback.answer("Нет прав для добавления предметов", show_alert=True)
        return
    await callback.message.answer("Выберите группу для добавления предмета:")
    await callback.answer()

@router.callback_query(F.data.startswith("subject_group_"))
async def select_group_for_subject(callback: CallbackQuery):
    group_id = int(callback.data.replace("subject_group_", ""))
    await callback.message.answer("Введите название предмета:")
    await callback.answer()

@router.message(F.text)
async def subject_name_handler(message: Message, state: FSMContext):
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == message.from_user.id))
        members = result.scalars().all()
    if not members:
        return
    for member in members:
        if can_manage_queue(member):
            subject = await add_subject(member.group_id, message.text.strip())
            await message.answer(f"✅ Предмет <b>{subject.name}</b> добавлен!", parse_mode="HTML")
            await state.clear()
            return

@router.callback_query(F.data.startswith("subject_"))
async def subject_details_handler(callback: CallbackQuery):
    subject_id = int(callback.data.replace("subject_", ""))
    subject = await get_subject_by_id(subject_id)
    if not subject:
        await callback.answer("Предмет не найден", show_alert=True)
        return
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == subject.group_id,
                GroupMember.user_id == callback.from_user.id
            )
        )
        member = result.scalar_one_or_none()
    can_manage = member and can_manage_queue(member)
    await callback.message.answer(
        f"📖 <b>{subject.name}</b>",
        parse_mode="HTML",
        reply_markup=get_subject_actions_keyboard(subject_id, subject.group_id, can_manage)
    )
    await callback.answer()