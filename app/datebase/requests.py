from app.datebase.models import async_session, Note, User, Birthday
from sqlalchemy import select, insert, update, delete
from datetime import datetime, timedelta, date

my_time = datetime.now().strftime("%d.%m.%Y")
data = datetime.now()
delta_days = data + timedelta(days=3)
data = str(data.strftime("%d-%m"))
delta_days = str(delta_days.strftime("%d-%m"))


async def get_data(day: str, month: str):
    day = int(day.lstrip('0'))
    month = int(month.lstrip('0'))
    teachers_day = date(datetime.now().year, month, day)
    today = date.today()
    if teachers_day >= today:
        return (teachers_day - today).days
    else:
        teachers_day = date(datetime.now().year + 1, month, day)
        return (teachers_day - today).days


async def calculate_age(born):
    day, month, year = map(int, born.split('.'))
    born = datetime(year, month, day)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


async def get_age_suffix(age: int) -> str:
    if 11 <= age % 100 <= 14:
        return "лет"
    last_digit = age % 10
    if last_digit == 1:
        return "год"
    if 2 <= last_digit <= 4:
        return "года"
    return "лет"


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


async def db_select(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.tg_id == tg_id).order_by(Birthday.delta_time))
        people = result.scalars().all()

        del_dict = {idx: (person.surname, person.name, person.date) for idx, person in enumerate(people, 1)}
        return del_dict


async def delete_one(tg_id, surname, name, date):
    async with async_session() as session:
        await session.execute(delete(Birthday).where(Birthday.tg_id == tg_id).where(Birthday.surname == surname)
                              .where(Birthday.name == name).where(Birthday.date == date))
        await session.commit()


async def update_surname(tg_id, surname, name, new_surname):
    async with async_session() as session:
        await session.execute(update(Birthday).where(Birthday.tg_id == tg_id).where(Birthday.surname == surname)
                              .where(Birthday.name == name).values(surname=new_surname))
        await session.commit()


async def update_name(tg_id, surname, name, new_name):
    async with async_session() as session:
        await session.execute(update(Birthday).where(Birthday.tg_id == tg_id).where(Birthday.surname == surname)
                              .where(Birthday.name == name).values(name=new_name))
        await session.commit()


async def update_date(tg_id, surname, name, new_date):
    split_data = new_date.split('.')
    data_get = await get_data(split_data[0], split_data[1])
    data_age = await calculate_age(new_date)
    async with async_session() as session:
        await session.execute(update(Birthday).where(Birthday.tg_id == tg_id).where(Birthday.surname == surname)
                              .where(Birthday.name == name).values(date=new_date, delta_time=data_get, age=data_age))
        await session.commit()


async def birthday_view():
    async with async_session() as session:
        result = await session.execute(select(Birthday).order_by(Birthday.delta_time))
        people = result.scalars().all()
        output = ""
        for person in people:
            output += (f"{person.surname} {person.name} - {person.age} {await get_age_suffix(person.age)}, "
                       f"до ДР: {person.delta_time} дней\n")
        return output


async def birthday_select():
    async with async_session() as session:
        result = await session.execute(select(Birthday).order_by(Birthday.delta_time))
        people = result.scalars().all()
        output = ""
        for person in people:
            output += f"{person.surname} {person.name} - {person.date}\n"
        return output


async def birthday():
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.delta_time == 0))
        people = result.scalars().all()
        if people:
            data_txt = "Сегодня у\n"
            for el in people:
                data_txt += f"{el.surname} {el.name}\nдень рождения!!!\nне забудьте поздравить!\n"
            return data_txt
        return "none"


async def birthday_reminder():
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.delta_time == 3))
        people = result.scalars().all()
        if people:
            data_txt = "Сегодня у\n"
            for el in people:
                data_txt += f"{el.surname} {el.name}\nдень рождения!!!\nне забудьте поздравить!\n"
            return data_txt
        return "none"


async def delta_db(e):
    async with async_session() as session:
        result = await session.execute(select(Birthday).where(Birthday.delta_time == 3))
        people = result.scalars().all()
        for el in people:
            tmp = str(el.date).split('.')
            data_get = await get_data(tmp[0], tmp[1])
            data_age = await calculate_age(el.date)
            await session.execute(
                update(Birthday).where(Birthday.surname == el.surname).where(Birthday.name == el.name)).values(
                delta_time=data_get, age=data_age)

            await session.commit()


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(get_age_suffix(18)))
    # asyncio.run(set_user(428030603))
    # asyncio.run(update_note_name(428030603, "new_name_1", "note_name_1", "note_text_1"))
    # asyncio.run(note_delete(428030603, "new_name_1", "note_text_1"))
    # asyncio.run(note_view())
    # asyncio.run(delete_select(428030603))
