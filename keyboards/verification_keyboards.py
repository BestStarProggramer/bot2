from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_students_keyboard(students, group_id=None):
    buttons = []
    for student in students:
        buttons.append([
            InlineKeyboardButton(text=f"👤 {student.full_name}", callback_data=f"claim_{student.id}")
        ])
    if group_id:
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_{group_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_verification_keyboard(student_id, user_id, approved=True):
    if approved:
        buttons = [
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"verify_ok_{user_id}_{student_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"verify_no_{user_id}_{student_id}")
            ]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_claim_keyboard(group_id):
    buttons = [
        [InlineKeyboardButton(text="📋 Выбрать из списка", callback_data=f"claim_list_{group_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_{group_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pending_claims_keyboard(claims, group_id):
    buttons = []
    for student, user in claims:
        buttons.append([
            InlineKeyboardButton(
                text=f"🔔 {student.full_name} (@{user.username})",
                callback_data=f"view_claim_{student.id}_{user.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_{group_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)