from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📅 Календарь", callback_data="view_calendar")],
        [InlineKeyboardButton(text="👤 Привязать ФИО", callback_data="claim_student")],
        [InlineKeyboardButton(text="👥 Мои группы", callback_data="my_groups")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_gender_keyboard(join_code: str = "none"):
    buttons = [
        [InlineKeyboardButton(text="👨 Мужской", callback_data=f"set_gender_male_{join_code}")],
        [InlineKeyboardButton(text="👩 Женский", callback_data=f"set_gender_female_{join_code}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard(callback_data: str = "main_menu"):
    buttons = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📅 Календарь", callback_data="view_calendar")],
        [InlineKeyboardButton(text="👥 Мои группы", callback_data="my_groups")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="view_profile")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)