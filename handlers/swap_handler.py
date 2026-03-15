from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from services.swap_service import create_swap_request, accept_swap_request, reject_swap_request, get_pending_swaps, get_swap_details, get_lab_students_for_swap
from services.user_service import get_or_create_user
from services.lab_service import get_lab_details
from services.permission_service import can_manage_queue
from keyboards.swap_keyboards import get_swap_keyboard, get_swap_request_keyboard, get_pending_swaps_keyboard
from database import SessionLocal
from models import User, SwapRequest, Lab
from sqlalchemy import select

router = Router()

@router.callback_query(F.data.startswith("swap_lab_"))
async def swap_lab_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("swap_lab_", ""))
    students = await get_lab_students_for_swap(lab_id, callback.from_user.id)
    if not students:
        await callback.answer("Нет доступных студентов для обмена", show_alert=True)
        return
    await callback.message.answer("Выберите студента для обмена:", reply_markup=get_swap_keyboard(lab_id, students, callback.from_user.id))
    await callback.answer()

@router.callback_query(F.data.startswith("swap_select_"))
async def swap_select_handler(callback: CallbackQuery):
    parts = callback.data.replace("swap_select_", "").split("_")
    lab_id = int(parts[0])
    target_user_id = int(parts[1])
    try:
        swap = await create_swap_request(lab_id, callback.from_user.id, target_user_id)
        await callback.message.answer("✅ Заявка отправлена! Ожидайте подтверждения.")
        
        async with SessionLocal() as session:
            result = await session.execute(select(User).where(User.telegram_id == target_user_id))
            target_user = result.scalar_one_or_none()
        
        if target_user:
            await callback.message.bot.send_message(
                target_user.telegram_id,
                f"🔄 <b>Заявка на обмен местами</b>\n\n"
                f"Пользователь @{callback.from_user.username} хочет поменяться с вами местами.\n\n"
                f"Лабораторная ID: {lab_id}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Принять", callback_data=f"swap_accept_{swap.id}"),
                        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"swap_reject_{swap.id}")
                    ]
                ])
            )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("swap_accept_"))
async def swap_accept_handler(callback: CallbackQuery):
    swap_id = int(callback.data.replace("swap_accept_", ""))
    try:
        await accept_swap_request(swap_id, callback.from_user.id)
        await callback.message.answer("✅ Обмен выполнен!")
        
        async with SessionLocal() as session:
            swap = await session.get(SwapRequest, swap_id)
            if swap:
                from_user = await session.execute(select(User).where(User.id == swap.from_user))
                from_user = from_user.scalar_one_or_none()
                if from_user:
                    await callback.message.bot.send_message(
                        from_user.telegram_id,
                        f"✅ Ваш обмен местами принят!"
                    )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("swap_reject_"))
async def swap_reject_handler(callback: CallbackQuery):
    swap_id = int(callback.data.replace("swap_reject_", ""))
    try:
        await reject_swap_request(swap_id, callback.from_user.id)
        await callback.message.answer("❌ Обмен отклонён")
        
        async with SessionLocal() as session:
            swap = await session.get(SwapRequest, swap_id)
            if swap:
                from_user = await session.execute(select(User).where(User.id == swap.from_user))
                from_user = from_user.scalar_one_or_none()
                if from_user:
                    await callback.message.bot.send_message(
                        from_user.telegram_id,
                        f"❌ Ваш обмен местами отклонён."
                    )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "view_pending_swaps")
async def view_pending_swaps_handler(callback: CallbackQuery):
    swaps = await get_pending_swaps(callback.from_user.id)
    if not swaps:
        await callback.answer("Нет pending заявок", show_alert=True)
        return
    await callback.message.answer("📋 Ваши заявки на обмен:", reply_markup=get_pending_swaps_keyboard(swaps))
    await callback.answer()

@router.callback_query(F.data.startswith("view_swap_"))
async def view_swap_handler(callback: CallbackQuery):
    swap_id = int(callback.data.replace("view_swap_", ""))
    details = await get_swap_details(swap_id)
    if not details:
        await callback.answer("Заявка не найдена", show_alert=True)
        return
    text = f"🔄 <b>Заявка на обмен</b>\n\n"
    text += f"От: {details['from_name']}\n"
    text += f"Лабораторная: {details['lab_subject']}\n"
    text += f"Дата: {details['lab_date'].strftime('%d.%m %H:%M') if details['lab_date'] else 'Не указана'}\n"
    buttons = [
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"swap_accept_{swap_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"swap_reject_{swap_id}")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="view_pending_swaps")]
    ]
    await callback.message.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()