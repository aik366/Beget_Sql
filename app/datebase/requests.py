from app.datebase.models import async_session, Note, User, Birthday
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta
from app.func import get_data, calculate_age, get_age_suffix

my_time = datetime.now().strftime("%d.%m.%Y")
data = datetime.now()
delta_days = data + timedelta(days=3)
data = str(data.strftime("%d-%m"))
delta_days = str(delta_days.strftime("%d-%m"))


async def set_user(tg_id, full_name):
    async with async_session() as session:
        user = await session.scalar(select(User.tg_id).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, full_name=full_name, data=my_time))
            await session.commit()


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


async def get_birthday(surname, name):
    surname, name = surname.capitalize(), name.capitalize()
    async with async_session() as session:
        cur = await session.execute(select(Birthday).where(Birthday.surname == surname).where(Birthday.name == name))
        return cur.scalar() is not None


async def add_birthday(tg_id, surname, name, date):
    split_data = date.split('.')
    data_get = await get_data(split_data[0], split_data[1])
    data_age = await calculate_age(date)
    async with async_session() as session:
        await session.execute(insert(Birthday).values(tg_id=tg_id, surname=surname.capitalize(), name=name.capitalize(),
                                                      date=date, delta_time=data_get, age=data_age))
        await session.commit()


async def delete_select(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.tg_id == tg_id).order_by(Birthday.id))
        people = result.scalars().all()

        del_dict = {idx: (person.surname, person.name, person.date) for idx, person in enumerate(people, 1)}
        return del_dict


async def delete_one(tg_id, surname, name, date):
    async with async_session() as session:
        await session.execute(delete(Birthday).where(Birthday.tg_id == tg_id).where(Birthday.surname == surname)
                              .where(Birthday.name == name).where(Birthday.date == date))
        await session.commit()


async def birthday_view(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.tg_id == tg_id).order_by(Birthday.id))
        people = result.scalars().all()
        output = ""
        for idx, person in enumerate(people, 1):
            output += f"{idx}. {person.surname} {person.name} {person.age} {get_age_suffix(person.age)}\n"
        return output


async def birthday_delta_view(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.tg_id == tg_id).order_by(Birthday.id))
        people = result.scalars().all()


if __name__ == '__main__':
    import asyncio

    # asyncio.run(set_user(428030603))
    # asyncio.run(update_note_name(428030603, "new_name_1", "note_name_1", "note_text_1"))
    # asyncio.run(note_delete(428030603, "new_name_1", "note_text_1"))
    # asyncio.run(note_view())
    # asyncio.run(delete_select(428030603))
