from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_swap_keyboard(lab_id, students, current_user_id):
    buttons = []
    for student in students:
        if student.user_id != current_user_id:
            name = student.full_name if student.full_name else student.username
            buttons.append([
                InlineKeyboardButton(text=f"🔄 {name}", callback_data=f"swap_select_{lab_id}_{student.user_id}")
            ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"lab_{lab_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_swap_request_keyboard(swap_id, from_name, to_position, from_position, lab_name):
    buttons = [
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"swap_accept_{swap_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"swap_reject_{swap_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_swap_confirmation_keyboard(lab_id, current_user_id):
    buttons = [
        [InlineKeyboardButton(text="📋 Выбрать студента", callback_data=f"swap_select_list_{lab_id}_{current_user_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"lab_{lab_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pending_swaps_keyboard(swaps):
    buttons = []
    for swap in swaps:
        buttons.append([
            InlineKeyboardButton(
                text=f"🔄 Заявка #{swap.id}",
                callback_data=f"view_swap_{swap.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)