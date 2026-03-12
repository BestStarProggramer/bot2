from sqlalchemy import select
from database import SessionLocal
from models import User


async def get_or_create_user(tg_user):
    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(User.telegram_id == tg_user.id)
        )

        user = result.scalar_one_or_none()

        if user:
            user.username = tg_user.username
            user.first_name = tg_user.first_name
            user.last_name = tg_user.last_name

            await session.commit()
            return user

        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name
        )

        session.add(user)
        await session.commit()

        return user

async def update_user_gender(user_id: int, gender: str):
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.gender = gender
                await session.commit()
            else:
                pass