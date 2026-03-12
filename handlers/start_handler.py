from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from services.user_service import get_or_create_user, update_user_gender
from services.group_service import get_group_by_code, join_group
from services.permission_service import can_create_group

from keyboards.common_keyboards import (
    get_start_keyboard, 
    get_payment_keyboard, 
    get_gender_keyboard
)

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    user = await get_or_create_user(message.from_user)
    
    args = message.text.split()
    join_code = args[1].replace("join_", "") if len(args) > 1 and args[1].startswith("join_") else "none"

    if user.gender == "unknown":
        await message.answer(
            "Чтобы слова правильно склонялись, надо выбрать пол:",
            reply_markup=get_gender_keyboard(join_code)
        )
        return

    if join_code != "none":
        group = await get_group_by_code(join_code)
        if group:
            await join_group(group.id, user.id)
            ending = "л" if user.gender == "male" else "ла"
            await message.answer(f"Ты успешно вступи{ending} в группу <b>{group.name}</b>!", parse_mode="HTML")
        else:
            await message.answer("Ссылка-приглашение недействительна.")

    await message.answer(
        "<b>ЗнайСвоёМесто!</b>\n\n"
        "Версия 3.0\n"
        "Используй меню ниже для управления группами:",
        parse_mode="HTML",
        reply_markup=get_start_keyboard()
    )

@router.callback_query(F.data.startswith("set_gender_"))
async def set_gender_handler(callback: CallbackQuery):
    parts = callback.data.split("_")
    new_gender = parts[2] 
    join_code = parts[3] if parts[3] != "none" else None

    await update_user_gender(callback.from_user.id, new_gender)
    
    await callback.message.delete()
    
    if join_code:
        group = await get_group_by_code(join_code)
        if group:
            await join_group(group.id, callback.from_user.id)
            await callback.message.answer(f"Настройки сохранены! Ты в группе <b>{group.name}</b>", parse_mode="HTML")

    await callback.message.answer(
        "Я запомнил твой выбор...",
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "try_create_group")
async def try_create_group_handler(callback: CallbackQuery):
    user = await get_or_create_user(callback.from_user)
    
    if can_create_group(user):
        await callback.message.answer("Введи название для твоей новой группы:")
        await callback.answer()
    else:
        await callback.message.edit_text(
            "🔒 Создание собственных групп доступно только по подписке.\n\n"
            "Приобрети доступ, чтобы стать старостой и управлять очередями своей группы.",
            reply_markup=get_payment_keyboard()
        )
        await callback.answer()

@router.callback_query(F.data == "stub_payment")
async def stub_payment_handler(callback: CallbackQuery):
    await callback.answer(
        "Оплата пока не настроена. Для получения доступа к функционалу обратитесь к владельцу бота напрямую.",
        show_alert=True
    )