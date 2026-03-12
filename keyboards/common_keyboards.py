from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="➕ Создать группу", callback_data="try_create_group"),
        ],
        [
            InlineKeyboardButton(text="🔗 Вступить в группу", callback_data="try_join_group")
        ]

    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_keyboard():
    buttons = [
        [InlineKeyboardButton(text="💳 Купить премиум", callback_data="stub_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_gender_keyboard(join_code: str = "none"):
    buttons = [
        [
            InlineKeyboardButton(text="Обожаю пиво с креветками и книги по Warhammer40k", callback_data=f"set_gender_male_{join_code}"),
            
        ],
        [
            InlineKeyboardButton(text="ЖЕНЩИНА!!!!", callback_data=f"set_gender_female_{join_code}")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)