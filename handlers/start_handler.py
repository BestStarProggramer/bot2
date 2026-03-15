from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.user_service import get_or_create_user, update_user_gender
from services.group_service import get_group_by_code, join_group
from services.permission_service import can_create_group
from keyboards.common_keyboards import get_start_keyboard, get_gender_keyboard, get_main_menu_keyboard

router = Router()

class GenderState(StatesGroup):
    waiting_for_gender = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user = await get_or_create_user(message.from_user)
    args = message.text.split()
    join_code = args[1].replace("join_", "") if len(args) > 1 and args[1].startswith("join_") else None

    if user.gender == "unknown":
        await message.answer(
            "Чтобы слова правильно склонялись, надо выбрать пол:",
            reply_markup=get_gender_keyboard(join_code if join_code else "none")
        )
        return

    if join_code:
        group = await get_group_by_code(join_code)
        if group:
            await join_group(group.id, user.id)
            ending = "л" if user.gender == "male" else "ла"
            await message.answer(f"Ты успешно вступи{ending} в группу <b>{group.name}</b>!", parse_mode="HTML")

    await message.answer(
        "<b>ЗнайСвоёМесто!</b>\n\nВерсия 3.0",
        parse_mode="HTML",
        reply_markup=get_start_keyboard()
    )

@router.callback_query(F.data.startswith("set_gender_"))
async def set_gender_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    new_gender = parts[2]
    join_code = parts[3] if len(parts) > 3 and parts[3] != "none" else None

    await update_user_gender(callback.from_user.id, new_gender)
    await callback.message.delete()

    if join_code:
        group = await get_group_by_code(join_code)
        if group:
            await join_group(group.id, callback.from_user.id)
            await callback.message.answer(f"Настройки сохранены! Ты в группе <b>{group.name}</b>", parse_mode="HTML")

    await callback.message.answer("Я запомнил твой выбор...", reply_markup=get_start_keyboard())
    await callback.answer()

@router.callback_query(F.data == "try_create_group")
async def try_create_group_handler(callback: CallbackQuery):
    user = await get_or_create_user(callback.from_user)
    if can_create_group(user):
        await callback.message.answer("Введи название для твоей новой группы:")
    else:
        await callback.message.answer("🔒 Создание групп доступно по подписке.")
    await callback.answer()

@router.callback_query(F.data == "my_groups")
async def my_groups_handler(callback: CallbackQuery):
    from services.group_service import get_user_groups
    groups = await get_user_groups(callback.from_user.id)
    if not groups:
        await callback.answer("Вы не состоите ни в одной группе", show_alert=True)
        return
    from keyboards.group_keyboards import get_group_list_keyboard
    await callback.message.answer("Ваши группы:", reply_markup=get_group_list_keyboard(groups))
    await callback.answer()

@router.callback_query(F.data == "view_calendar")
async def view_calendar_handler(callback: CallbackQuery):
    from services.group_service import get_user_groups
    from services.lab_service import get_group_labs
    from keyboards.lab_keyboards import get_labs_keyboard
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id))
        members = result.scalars().all()
    if not members:
        await callback.answer("Вы не состоите ни в одной группе", show_alert=True)
        return
    group_id = members[0].group_id
    labs = await get_group_labs(group_id)
    if not labs:
        await callback.message.answer("📅 Нет запланированных лабораторных")
        await callback.answer()
        return
    await callback.message.answer("📅 Календарь лабораторных:", reply_markup=get_labs_keyboard(labs))
    await callback.answer()

@router.callback_query(F.data == "claim_student")
async def claim_student_handler(callback: CallbackQuery):
    from services.group_service import get_user_groups
    from services.verification_service import get_group_students
    from keyboards.verification_keyboards import get_students_keyboard
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id))
        members = result.scalars().all()
    if not members:
        await callback.answer("Вы не состоите ни в одной группе", show_alert=True)
        return
    group_id = members[0].group_id
    students = await get_group_students(group_id)
    if not students:
        await callback.answer("Нет студентов в группе", show_alert=True)
        return
    await callback.message.answer("Выберите ваше ФИО:", reply_markup=get_students_keyboard(students))
    await callback.answer()

@router.callback_query(F.data == "view_profile")
async def view_profile_handler(callback: CallbackQuery):
    from services.user_service import get_or_create_user
    user = await get_or_create_user(callback.from_user)
    text = f"👤 <b>Профиль</b>\n\n"
    text += f"ID: {user.telegram_id}\n"
    text += f"Username: @{user.username}\n"
    text += f"Имя: {user.first_name} {user.last_name}\n"
    text += f"Пол: {'Мужской' if user.gender == 'male' else 'Женский' if user.gender == 'female' else 'Не указан'}\n"
    text += f"Premium: {'✅' if user.is_premium else '❌'}\n"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = "<b>Справка по боту</b>\n\n"
    text += "/start - Главное меню\n"
    text += "/help - Эта справка\n"
    text += "\nФункции:\n"
    text += "📅 Календарь - просмотр лабораторных\n"
    text += "👤 Привязать ФИО - верификация студента\n"
    text += "👥 Мои группы - управление группами"
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())