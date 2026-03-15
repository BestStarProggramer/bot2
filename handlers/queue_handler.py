from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from services.queue_service import generate_queue_for_lab, get_queue_details
from services.permission_service import can_manage_queue
from keyboards.queue_keyboards import get_queue_keyboard, get_generate_queue_keyboard

router = Router()

@router.callback_query(F.data.startswith("generate_queue_"))
async def generate_queue_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("generate_queue_", ""))
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember, Lab
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id))
        member = result.scalar_one_or_none()
    if not member or not can_manage_queue(member):
        await callback.answer("Нет прав", show_alert=True)
        return
    try:
        queue = await generate_queue_for_lab(lab_id, callback.from_user.id)
        await callback.message.answer("✅ Очередь сгенерирована!")
        await callback.message.answer(
            f"📋 Очередь сформирована\nЛабораторная ID: {lab_id}",
            reply_markup=get_queue_keyboard(queue.id if queue else lab_id, lab_id, True)
        )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("view_queue_"))
async def view_queue_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("view_queue_", ""))
    queue = await get_queue_details(lab_id)
    if not queue:
        await callback.answer("Очередь не найдена или ещё не сгенерирована", show_alert=True)
        return
    text = "📋 <b>Очередь:</b>\n\n"
    current_priority = None
    for entry in queue["entries"]:
        if entry["priority_group"] != current_priority:
            current_priority = entry["priority_group"]
            text += f"\n⚡ Приоритет {current_priority}:\n"
        text += f"{entry['position']}. {entry['name']} — {entry['weight']:.2f}\n"
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember, Lab
    async with SessionLocal() as session:
        lab_result = await session.execute(select(Lab).where(Lab.id == lab_id))
        lab = lab_result.scalar_one_or_none()
        member_result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == lab.group_id if lab else 0,
                GroupMember.user_id == callback.from_user.id
            )
        )
        member = member_result.scalar_one_or_none()
    can_manage = member and can_manage_queue(member)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_queue_keyboard(queue.get("id", lab_id), lab_id, can_manage))
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_generate_"))
async def confirm_generate_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("confirm_generate_", ""))
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id))
        member = result.scalar_one_or_none()
    if not member or not can_manage_queue(member):
        await callback.answer("Нет прав", show_alert=True)
        return
    try:
        queue = await generate_queue_for_lab(lab_id, callback.from_user.id)
        await callback.message.edit_text("✅ Очередь сгенерирована!")
        await view_queue_handler(callback)
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("close_lab_"))
async def close_lab_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("close_lab_", ""))
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember, Lab
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id))
        member = result.scalar_one_or_none()
    if not member or not can_manage_queue(member):
        await callback.answer("Нет прав", show_alert=True)
        return
    from services.lab_service import close_lab
    lab = await close_lab(lab_id)
    await callback.message.answer(f"🔒 Лабораторная закрыта\n{lab.date.strftime('%d.%m %H:%M') if lab and lab.date else ''}")
    await callback.answer()

@router.callback_query(F.data.startswith("lab_priorities_"))
async def lab_priorities_handler(callback: CallbackQuery):
    lab_id = int(callback.data.replace("lab_priorities_", ""))
    from services.lab_service import get_lab_priorities
    priorities = await get_lab_priorities(lab_id)
    text = "⚙️ <b>Приоритеты лабораторной:</b>\n\n"
    for prio in priorities:
        text += f"{prio.emoji} {prio.name} — Значение: {prio.priority_value}, Влияет на вес: {'✅' if prio.affects_weight else '❌'}\n"
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить приоритет", callback_data=f"add_priority_{lab_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_lab_{lab_id}")]
    ]
    await callback.message.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()