from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_labs_keyboard(labs):
    buttons = []
    for lab in labs:
        date_str = lab.date.strftime("%d.%m %H:%M") if lab.date else "Дата не указана"
        buttons.append([
            InlineKeyboardButton(text=f"📚 {lab.subject.name} — {date_str}", callback_data=f"lab_{lab.id}")
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="view_calendar")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lab_details_keyboard(lab_id, is_registered, is_closed, can_manage=False):
    buttons = []
    
    if not is_closed:
        if not is_registered:
            buttons.append([InlineKeyboardButton(text="📝 Записаться", callback_data=f"join_lab_{lab_id}")])
        else:
            buttons.append([InlineKeyboardButton(text="🔄 Обмен местами", callback_data=f"swap_lab_{lab_id}")])
            buttons.append([InlineKeyboardButton(text="❌ Покинуть очередь", callback_data=f"leave_lab_{lab_id}")])
    
    if can_manage and not is_closed:
        buttons.append([InlineKeyboardButton(text="⚙️ Управление", callback_data=f"admin_lab_{lab_id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="view_calendar")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lab_admin_keyboard(lab_id, group_id):
    buttons = [
        [InlineKeyboardButton(text="⚙️ Приоритеты", callback_data=f"lab_priorities_{lab_id}")],
        [InlineKeyboardButton(text="🎲 Генерировать очередь", callback_data=f"generate_queue_{lab_id}")],
        [InlineKeyboardButton(text="📋 Просмотр очереди", callback_data=f"view_queue_{lab_id}")],
        [InlineKeyboardButton(text="🔒 Закрыть лабораторную", callback_data=f"close_lab_{lab_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_labs_{group_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_priority_selection_keyboard(priorities, lab_id):
    buttons = []
    for priority in priorities:
        buttons.append([
            InlineKeyboardButton(
                text=f"{priority.emoji} {priority.name} (×{priority.priority_value})",
                callback_data=f"select_priority_{priority.id}_{lab_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"lab_{lab_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lab_calendar_keyboard(labs, group_id):
    buttons = []
    for lab in labs:
        date_str = lab.date.strftime("%d.%m.%Y %H:%M") if lab.date else "Дата не указана"
        buttons.append([
            InlineKeyboardButton(text=f"{lab.subject.name} — {date_str}", callback_data=f"lab_{lab.id}")
        ])
    buttons.append([
        InlineKeyboardButton(text="➕ Создать лабораторную", callback_data=f"create_lab_{group_id}")
    ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_{group_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_create_lab_keyboard(group_id):
    buttons = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_labs_{group_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_priority_config_keyboard(lab_id, group_id):
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить приоритет", callback_data=f"add_priority_{lab_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_lab_{lab_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)