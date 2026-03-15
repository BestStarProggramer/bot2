from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from services.verification_service import add_student_to_group, get_group_students, claim_student, verify_student, get_pending_claims
from keyboards.verification_keyboards import get_students_keyboard, get_verification_keyboard, get_pending_claims_keyboard

router = Router()

@router.callback_query(F.data == "claim_student")
async def claim_student_handler(callback: CallbackQuery):
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

@router.callback_query(F.data.startswith("claim_"))
async def claim_confirm_handler(callback: CallbackQuery):
    student_id = int(callback.data.replace("claim_", ""))
    try:
        await claim_student(student_id, callback.from_user.id)
        await callback.message.answer("✅ Заявка отправлена старосте! Ожидайте подтверждения.")
        from config import ADMINS
        from services.group_service import get_group_headmen
        from services.user_service import get_or_create_user
        from database import SessionLocal
        from sqlalchemy import select
        from models import AcademicStudent, GroupMember, User
        async with SessionLocal() as session:
            student = await session.get(AcademicStudent, student_id)
            if student:
                headmen = await get_group_headmen(student.group_id)
                for hm in headmen:
                    hm_user = await session.get(User, hm.user_id)
                    if hm_user:
                        await callback.message.bot.send_message(
                            hm_user.telegram_id,
                            f"🔔 <b>Заявка на привязку</b>\n\n"
                            f"Пользователь @{callback.from_user.username} хочет быть:\n"
                            f"<b>{student.full_name}</b>\n\n"
                            f"[✅ Подтвердить] [❌ Отклонить]",
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="✅", callback_data=f"verify_ok_{callback.from_user.id}_{student_id}"),
                                    InlineKeyboardButton(text="❌", callback_data=f"verify_no_{callback.from_user.id}_{student_id}")
                                ]
                            ])
                        )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("verify_ok_"))
async def verify_ok_handler(callback: CallbackQuery):
    parts = callback.data.replace("verify_ok_", "").split("_")
    user_id = int(parts[0])
    student_id = int(parts[1])
    try:
        await verify_student(user_id, student_id, True)
        await callback.message.answer("✅ Подтверждено!")
        from services.user_service import get_or_create_user
        from database import SessionLocal
        from sqlalchemy import select
        from models import User
        async with SessionLocal() as session:
            user = await session.get(User, user_id)
            if user:
                await callback.message.bot.send_message(
                    user.telegram_id,
                    f"✅ Ваша привязка к студенту подтверждена старостой!"
                )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("verify_no_"))
async def verify_no_handler(callback: CallbackQuery):
    parts = callback.data.replace("verify_no_", "").split("_")
    user_id = int(parts[0])
    student_id = int(parts[1])
    try:
        await verify_student(user_id, student_id, False)
        await callback.message.answer("❌ Отклонено!")
        from services.user_service import get_or_create_user
        from database import SessionLocal
        from sqlalchemy import select
        from models import User
        async with SessionLocal() as session:
            user = await session.get(User, user_id)
            if user:
                await callback.message.bot.send_message(
                    user.telegram_id,
                    f"❌ Ваша привязка к студенту отклонена старостой."
                )
    except Exception as e:
        await callback.answer(str(e), show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("add_student_"))
async def add_student_start_handler(callback: CallbackQuery):
    group_id = int(callback.data.replace("add_student_", ""))
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == callback.from_user.id, GroupMember.group_id == group_id))
        member = result.scalar_one_or_none()
    if not member or member.role != "headman":
        await callback.answer("Нет прав", show_alert=True)
        return
    await callback.message.answer("Введите ФИО студента для добавления в список:")
    await callback.answer()

@router.message(F.text)
async def add_student_name_handler(message: Message):
    from database import SessionLocal
    from sqlalchemy import select
    from models import GroupMember
    async with SessionLocal() as session:
        result = await session.execute(select(GroupMember).where(GroupMember.user_id == message.from_user.id))
        members = result.scalars().all()
    if not members:
        return
    for member in members:
        if member.role == "headman":
            student = await add_student_to_group(member.group_id, message.text.strip())
            await message.answer(f"✅ Студент <b>{student.full_name}</b> добавлен в список!", parse_mode="HTML")
            return

@router.callback_query(F.data.startswith("view_claims_"))
async def view_claims_handler(callback: CallbackQuery):
    group_id = int(callback.data.replace("view_claims_", ""))
    claims = await get_pending_claims(group_id)
    if not claims:
        await callback.answer("Нет ожидающих заявок", show_alert=True)
        return
    await callback.message.answer("📋 Ожидающие заявки:", reply_markup=get_pending_claims_keyboard(claims, group_id))
    await callback.answer()