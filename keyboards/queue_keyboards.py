from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_queue_keyboard(queue_id, lab_id, can_manage=False):
    buttons = [
        [InlineKeyboardButton(text="🔄 Обновить", callback_data=f"view_queue_{lab_id}")]
    ]
    if can_manage:
        buttons.append([InlineKeyboardButton(text="⚙️ Управление", callback_data=f"admin_lab_{lab_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"lab_{lab_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_queue_actions_keyboard(lab_id):
    buttons = [
        [InlineKeyboardButton(text="🎲 Генерировать очередь", callback_data=f"generate_queue_{lab_id}")],
        [InlineKeyboardButton(text="📋 Просмотреть очередь", callback_data=f"view_queue_{lab_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_lab_{lab_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_generate_queue_keyboard(lab_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_generate_{lab_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_lab_{lab_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_queue_navigation_keyboard(queue_id, page=0):
    buttons = [
        [InlineKeyboardButton(text="◀️ Пред.", callback_data=f"queue_prev_{queue_id}_{page}")],
        [InlineKeyboardButton(text="След. ▶️", callback_data=f"queue_next_{queue_id}_{page}")]
    ]
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"view_queue_{queue_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)