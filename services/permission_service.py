from config import ADMINS


def is_bot_admin(user_id: int) -> bool:
    return user_id in ADMINS


def is_headman(member) -> bool:
    return member.role == "headman"


def is_assistant(member) -> bool:
    return member.role == "assistant"


def can_manage_queue(member) -> bool:
    return member.role in ["headman", "assistant"]