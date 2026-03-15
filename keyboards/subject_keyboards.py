from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subjects_keyboard(subjects, group_id):
    buttons = []
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(text=f"📖 {subject.name}", callback_data=f"subject_{subject.id}")
        ])
    buttons.append([InlineKeyboardButton(text="➕ Добавить предмет", callback_data=f"add_subject_{group_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_{group_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subject_actions_keyboard(subject_id, group_id, can_manage=False):
    buttons = [
        [InlineKeyboardButton(text="📅 Лабораторные по предмету", callback_data=f"subject_labs_{subject_id}")]
    ]
    if can_manage:
        buttons.append([InlineKeyboardButton(text="❌ Удалить предмет", callback_data=f"delete_subject_{subject_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_subjects_{group_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_add_subject_keyboard(group_id):
    buttons = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"group_subjects_{group_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)