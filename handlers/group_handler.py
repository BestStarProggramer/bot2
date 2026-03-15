from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.user_service import get_or_create_user
from services.group_service import create_group, get_user_groups, get_group_by_id, get_group_member
from services.permission_service import is_headman, is_assistant, can_manage_queue
from keyboards.group_keyboards import get_group_list_keyboard, get_group_admin_keyboard, get_group_member_keyboard

router = Router()

class GroupNameState(StatesGroup):
    waiting_for_name = State()

@router.callback_query(F.data == "my_groups")
async def my_groups_handler(callback: CallbackQuery):
    groups = await get_user_groups(callback.from_user.id)
    if not groups:
        await callback.answer("Вы не состоите ни в одной группе", show_alert=True)
        return
    await callback.message.answer("Ваши группы:", reply_markup=get_group_list_keyboard(groups))
    await callback.answer()

@router.callback_query(F.data.startswith("group_"))
async def group_details_handler(callback: CallbackQuery):
    group_id = int(callback.data.replace("group_", ""))
    group = await get_group_by_id(group_id)
    if not group:
        await callback.answer("Группа не найдена", show_alert=True)
        return
    
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
    
    text = f"<b>Группа:</b> {group.name}\n"
    text += f"Код приглашения: {group.invite_code}\n"
    text += f"Ссылка: https://t.me/{(await callback.message.bot.get_me()).username}?start=join_{group.invite_code}"
    
    if member and (is_headman(member) or is_assistant(member)):
        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_group_admin_keyboard(group_id))
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_group_member_keyboard(group_id, False))
    await callback.answer()

@router.callback_query(F.data.startswith("group_admin_"))
async def group_admin_handler(callback: CallbackQuery):
    group_id = int(callback.data.replace("group_admin_", ""))
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
    await callback.message.answer("Управление группой:", reply_markup=get_group_admin_keyboard(group_id))
    await callback.answer()

@router.callback_query(F.data.startswith("group_subjects_"))
async def group_subjects_handler(callback: CallbackQuery):
    from handlers.subject_handler import show_subjects_for_group
    group_id = int(callback.data.replace("group_subjects_", ""))
    await show_subjects_for_group(callback, group_id)

@router.callback_query(F.data.startswith("group_labs_"))
async def group_labs_handler(callback: CallbackQuery):
    from handlers.lab_handler import show_labs_for_group
    group_id = int(callback.data.replace("group_labs_", ""))
    await show_labs_for_group(callback, group_id)

@router.message(F.text, GroupNameState.waiting_for_name)
async def group_name_handler(message: Message, state: FSMContext):
    group_name = message.text.strip()
    user = await get_or_create_user(message.from_user)
    group = await create_group(user.id, group_name)
    invite_link = f"https://t.me/{(await message.bot.get_me()).username}?start=join_{group.invite_code}"
    await message.answer(
        f"✅ Группа <b>{group_name}</b> создана!\n\nПригласительная ссылка:\n{invite_link}",
        parse_mode="HTML"
    )
    await state.clear()