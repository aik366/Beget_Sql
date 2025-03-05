from app.datebase.models import async_session, Note, User, Birthday
from sqlalchemy import select, insert, update, delete
from datetime import datetime

my_time = datetime.now().strftime("%d.%m.%Y")


async def set_user(tg_id, full_name):
    async with async_session() as session:
        user = await session.scalar(select(User.tg_id).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, full_name=full_name, data=my_time))
            await session.commit()


# async def get_categories():
#     async with async_session() as session:
#         return await session.scalars(select(Category))
#
#
# async def get_item_by_category(category_id):
#     async with async_session() as session:
#         return await session.scalars(select(Item).where(Item.category == category_id))
#
#
# async def get_item(item_id):
#     async with async_session() as session:
#         return await session.scalar(select(Item).where(Item.id == item_id))


async def add_note(tg_id, note_name, note_text=None, note_type=None, file_id='----', note_date=my_time):
    async with async_session() as session:
        await session.execute(insert(Note).values(tg_id=tg_id, note_name=note_name, note_text=note_text,
                                                  note_type=note_type, file_id=file_id, note_date=note_date))
        await session.commit()


async def note_view(tg_id):
    async with async_session() as session:
        notes = await session.scalars(select(Note).where(Note.tg_id == tg_id))
    return {note.id: (note.note_type, note.note_name, note.note_text, note.file_id) for note in notes}


async def update_note_name(tg_id, new_name, note_name, note_text):
    async with async_session() as session:
        await session.execute(update(Note).where(Note.tg_id == tg_id).where(Note.note_name == note_name).where(
            Note.note_text == note_text).values(note_name=new_name))
        await session.commit()


async def update_note_text(tg_id, new_text, note_name, note_text):
    async with async_session() as session:
        await session.execute(update(Note).where(Note.tg_id == tg_id).where(Note.note_name == note_name).where(
            Note.note_text == note_text).values(note_text=new_text))
        await session.commit()


async def note_delete(tg_id, note_name, note_text):
    async with async_session() as session:
        await session.execute(delete(Note).where(Note.tg_id == tg_id).where(Note.note_name == note_name).where(
            Note.note_text == note_text))
        await session.commit()


async def get_birthday():
    async with async_session() as session:
        return await session.scalars(select(Birthday))


async def add_birthday(tg_id, surname, name, date):
    async with async_session() as session:
        await session.execute(insert(Birthday).values(tg_id=tg_id, surname=surname, name=name, date=date))
        await session.commit()


if __name__ == '__main__':
    import asyncio

    asyncio.run(set_user(428030603))
    # asyncio.run(update_note_name(428030603, "new_name_1", "note_name_1", "note_text_1"))
    # asyncio.run(note_delete(428030603, "new_name_1", "note_text_1"))
    asyncio.run(note_view())
