from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_group_list_keyboard(groups):
    buttons = []
    for group in groups:
        buttons.append([
            InlineKeyboardButton(text=f"📚 {group.name}", callback_data=f"group_{group.id}")
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_group_admin_keyboard(group_id):
    buttons = [
        [InlineKeyboardButton(text="📚 Предметы", callback_data=f"group_subjects_{group_id}")],
        [InlineKeyboardButton(text="📅 Лабораторные", callback_data=f"group_labs_{group_id}")],
        [InlineKeyboardButton(text="👥 Участники", callback_data=f"group_members_{group_id}")],
        [InlineKeyboardButton(text="➕ Добавить студента в список", callback_data=f"add_student_{group_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="my_groups")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_group_member_keyboard(group_id, is_headman=False):
    buttons = [
        [InlineKeyboardButton(text="📅 Календарь", callback_data=f"group_labs_{group_id}")],
        [InlineKeyboardButton(text="📚 Предметы", callback_data=f"group_subjects_{group_id}")]
    ]
    if is_headman:
        buttons.append([InlineKeyboardButton(text="⚙️ Управление", callback_data=f"group_admin_{group_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="my_groups")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_role_selection_keyboard(group_id, user_id):
    buttons = [
        [InlineKeyboardButton(text="👤 Студент", callback_data=f"set_role_student_{group_id}_{user_id}")],
        [InlineKeyboardButton(text="⭐ Помощник", callback_data=f"set_role_assistant_{group_id}_{user_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_members_{group_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_create_group_keyboard():
    buttons = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)