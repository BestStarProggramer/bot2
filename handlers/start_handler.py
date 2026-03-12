from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from ..services.user_service import get_or_create_user
from ..services.group_service import get_group_by_code, join_group

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    user = await get_or_create_user(message.from_user)

    args = message.text.split()

    if len(args) > 1 and args[1].startswith("join_"):

        code = args[1].replace("join_", "")

        group = await get_group_by_code(code)

        if not group:
            await message.answer("Приглашение недействительно")
            return

        await join_group(group.id, user.id)

        await message.answer(
            f"Ты вступил в группу {group.name}"
        )

        return

    await message.answer(
        "ЗнайСвоёМесто!\n\n"
        "Версия 3.0\n"
        "Создай группу или вступи по приглашению."
    )