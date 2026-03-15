import secrets
from sqlalchemy import select
from database import SessionLocal
from models import Group, GroupMember, User


def generate_invite_code():
    return secrets.token_hex(4)

async def create_group(name: str, creator_id: int):
    async with SessionLocal() as session:
        invite_code = generate_invite_code()
        
        new_group = Group(name=name, creator_id=creator_id, invite_code=invite_code)
        session.add(new_group)
        await session.flush()
        
        member = GroupMember(user_id=creator_id, group_id=new_group.id, role="admin")
        session.add(member)
        
        await session.commit()
        await session.refresh(new_group)
        return new_group

async def get_group_by_code(code):
    async with SessionLocal() as session:
        result = await session.execute(select(Group).where(Group.invite_code == code))
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
        member = GroupMember(group_id=group_id, user_id=user_id, role="student")
        session.add(member)
        await session.commit()
        return member

async def get_user_groups(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Group).join(GroupMember).where(GroupMember.user_id == user_id)
        )
        return result.scalars().all()

async def get_group_by_id(group_id):
    async with SessionLocal() as session:
        return await session.get(Group, group_id)

async def get_group_member(group_id, user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

async def set_member_role(group_id, user_id, role):
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )
        member = result.scalar_one_or_none()
        if member:
            member.role = role
            await session.commit()
        return member

async def get_group_headmen(group_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.role == "headman"
            )
        )
        return result.scalars().all()