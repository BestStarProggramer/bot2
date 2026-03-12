import secrets
from sqlalchemy import select

from database import SessionLocal
from models import Group, GroupMember


def generate_invite_code():
    return secrets.token_hex(4)


async def create_group(owner_id, name):

    async with SessionLocal() as session:

        code = generate_invite_code()

        group = Group(
            name=name,
            owner_id=owner_id,
            invite_code=code
        )

        session.add(group)
        await session.commit()
        await session.refresh(group)

        member = GroupMember(
            group_id=group.id,
            user_id=owner_id,
            role="headman"    
        )

        session.add(member)
        await session.commit()

        return group


async def get_group_by_code(code):

    async with SessionLocal() as session:

        result = await session.execute(
            select(Group).where(Group.invite_code == code)
        )

        return result.scalar_one_or_none()


async def join_group(group_id, user_id):

    async with SessionLocal() as session:

     
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            return existing

        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role="student"   
        )

        session.add(member)
        await session.commit()

        return member