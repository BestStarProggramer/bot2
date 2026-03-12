from config import ADMINS
from models import User

def is_bot_admin(user_id: int) -> bool:
    return user_id in ADMINS


def is_headman(member) -> bool:
    return member.role == "headman"


def is_assistant(member) -> bool:
    return member.role == "assistant"


def can_manage_queue(member) -> bool:
    return member.role in ["headman", "assistant"]

def can_create_group(user: User) -> bool:
    return user.is_premium or is_bot_admin(user.telegram_id)