from app.datebase.models import async_session, Note, User, Birthday
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta, date


async def admin_delete(surname, name):
    async with async_session() as session:
        await session.execute(delete(Birthday).where(Birthday.surname == surname).where(Birthday.name == name))
        await session.commit()


async def db_select_id():
    async with async_session() as session:
        result = await session.execute(select(User))
        people = result.scalars().all()
        return [(person.tg_id, person.full_name, person.data) for person in people]


async def db_id_select():
    async with async_session() as session:
        result = await session.execute(select(User))
        people = result.scalars().all()
        return [person.tg_id for person in people]


async def db_delete_id(tg_id):
    async with async_session() as session:
        await session.execute(delete(User).where(User.tg_id == tg_id))
        await session.commit()
