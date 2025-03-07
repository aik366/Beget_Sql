from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import MY_ID
from random import choice
from datetime import datetime
import app.func as fn
import os

import app.keyboards as kb
from app.datebase.requests import set_user
import app.datebase.requests as nt

router = Router()


class Form(StatesGroup):
    first_name = State()
    last_name = State()
    birthday = State()
    del_user = State()
    del_number = State()
    del_len_list = State()
    list_del = State()
    edit_number = State()
    edit_len_list = State()
    edit_surname = State()
    edit_name = State()
    edit_data = State()
    surname_edit = State()
    name_edit = State()
    data_edit = State()


def validate_name(name):
    return len(name) >= 2 and name.isalpha()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await set_user(message.from_user.id, message.from_user.full_name)
    if message.from_user.id != MY_ID:
        await bot.send_message(MY_ID, f'Пользователь {message.from_user.full_name} начал работу с ботом')
    await message.answer(f'Привет! {message.from_user.full_name}', reply_markup=kb.add_user_data)
    await state.clear()


@router.message(Command('help'))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer('Вы нажали на кнопку помощи')
    await state.clear()


@router.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != MY_ID:
        await message.answer('Вы не администратор')
        return
    await message.answer('Вы нажали на кнопку администратора', reply_markup=kb.admin)
    await state.clear()


@router.message(F.text == '🏠Главное меню')
async def start_menu(message: Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=kb.add_user_data)
    await state.clear()


@router.message(F.text == '❌Отмена')
async def add_cencel(message: Message, state: FSMContext):
    await message.answer("Действие отменено")
    await state.clear()


@router.message(F.text == '👁️Просмотр данных')
async def add_user_viev(message: Message, state: FSMContext):
    await message.answer(f"{await nt.birthday_view()}", reply_markup=kb.view_birthday)
    await state.clear()


@router.callback_query(F.data == 'birthday')
async def add_user_viev_data(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"{await nt.birthday_select()}", reply_markup=kb.add_user_data)
    await state.clear()
    await call.answer()


@router.message(F.text == '✨Пожелания')
async def open_wishes(message: Message):
    with open(f"files/wishes.txt", "r", encoding="utf-8") as f:
        wishes_txt = choice(f.read().split('\n'))
        await message.answer(f"{wishes_txt}")


@router.message(F.text == '🥂Тост')
async def open_toasts(message: Message):
    with open(f"files/toasts.txt", "r", encoding="utf-8") as f:
        toasts_txt = choice(f.read().split('\n'))
        await message.answer(f"{toasts_txt}")


@router.message(F.text == '🎁Открытки')
async def file_open_images(message: Message, state: FSMContext):
    img = FSInputFile(f'images/{choice(os.listdir("images"))}')
    await message.answer_photo(img)
    await state.clear()


@router.message(F.text == '🗑️Удалить данные')
async def delete_user(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.del_number)
    dict_del = await nt.db_select(message.from_user.id)
    await state.update_data(list_del=dict_del)
    await state.update_data(del_len_list=len(dict_del))

    output = ""
    for key, value in dict_del.items():
        output += f"{key} - {value[0]} {value[1]} {value[2]}\n"

    if dict_del:
        await message.answer(f"{output}\nВведите порядковый номер\nДля удаления данных")
    else:
        await message.answer('У вас нет данных для удаления', reply_markup=kb.add_user_data)
        await state.clear()


@router.message(F.text == '✏️Редактировать')
async def view_user(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.edit_number)
    dict_del = await nt.db_select(message.from_user.id)
    await state.update_data(list_del=dict_del)
    await state.update_data(del_len_list=len(dict_del))

    output = ""
    for key, value in dict_del.items():
        output += f"{key} - {value[0]} {value[1]} {value[2]}\n"

    if dict_del:
        await message.answer(f"{output}\nВведите порядковый номер\nДля редактирования данных")
    else:
        await message.answer('У вас нет данных для редактирования', reply_markup=kb.add_user_data)
        await state.clear()


@router.message(F.text == '🆕Добавить данные')
async def add_data(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.first_name)
    await message.answer("Введите имя (только буквы):", reply_markup=kb.cancel_one)


@router.message(F.text == '😂Анекдот дня')
async def open_wishes(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"{await fn.anekdot_random()}")


@router.message(F.text == '💲Курсы валют')
async def open_wishes(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"{await fn.currency()}")


@router.message(F.text == '🌦️Погода')
async def open_wishes(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"{await fn.get_weather_forecast()}")


@router.message(Form.del_number)
async def delete_user_reg(message: Message, state: FSMContext):
    await state.update_data(del_number=int(message.text))
    data_state = await state.get_data()
    if not message.text.isdigit() or int(message.text) > data_state['del_len_list'] or int(message.text) < 1:
        return await message.answer("Вы ввели неверное число\nПопробуйте ещё раз", reply_markup=kb.add_user_data)
    data_state = await state.get_data()
    surname, name, data = data_state['list_del'][int(message.text)]
    await message.answer(f'{surname} {name} {data}', reply_markup=kb.delete)


@router.callback_query(F.data == 'delete')
async def delete_user(call: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    surname, name, data = data_state['list_del'][data_state['del_number']]
    await nt.delete_one(call.from_user.id, surname, name, data)
    await call.message.answer('Данные удалены', reply_markup=kb.add_user_data)
    await state.clear()
    await call.answer()


@router.message(Form.edit_number)
async def view_user_reg(message: Message, state: FSMContext):
    await state.update_data(edit_number=int(message.text))
    data_state = await state.get_data()
    if not message.text.isdigit() or int(message.text) > data_state['del_len_list'] or int(message.text) < 1:
        return await message.answer("Вы ввели неверное число\nПопробуйте ещё раз", reply_markup=kb.add_user_data)
    data_state = await state.get_data()
    surname, name, data = data_state['list_del'][int(message.text)]
    await message.answer(f'{surname} {name} {data}', reply_markup=kb.edit)


@router.callback_query(F.data == 'surname')
async def edit_user(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.surname_edit)
    await call.message.answer("Введите новую фамилию (только буквы):")
    await call.answer()


@router.message(Form.surname_edit)
async def edit_user_reg(message: Message, state: FSMContext):
    if not validate_name(message.text):
        return await message.answer("Неверная фамилия! Используйте только буквы (мин. 2 символа).",
                                    reply_markup=kb.add_user_data)
    await state.update_data(surname_edit=message.text.capitalize())
    data_state = await state.get_data()
    surname, name, data = data_state['list_del'][data_state['edit_number']]
    await nt.update_surname(message.from_user.id, surname, name, data_state['surname_edit'])
    await message.answer('Данные изменены', reply_markup=kb.add_user_data)
    await state.clear()


@router.callback_query(F.data == 'name')
async def edit_user(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.name_edit)
    await call.message.answer("Введите новое имя (только буквы):")
    await call.answer()


@router.message(Form.name_edit)
async def edit_user_reg(message: Message, state: FSMContext):
    if not validate_name(message.text):
        return await message.answer("Неверная имя! Используйте только буквы (мин. 2 символа).",
                                    reply_markup=kb.add_user_data)
    await state.update_data(name_edit=message.text.capitalize())
    data_state = await state.get_data()
    surname, name, data = data_state['list_del'][data_state['edit_number']]
    await nt.update_name(message.from_user.id, surname, name, data_state['name_edit'])
    await message.answer('Данные изменены', reply_markup=kb.add_user_data)
    await state.clear()


@router.callback_query(F.data == 'date')
async def edit_user(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.data_edit)
    await call.message.answer("Введите новую дату\nВ формате ДД.ММ.ГГГГ:")
    await call.answer()


@router.message(Form.data_edit)
async def edit_user_reg(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.replace(",", "."), "%d.%m.%Y").date()
    except ValueError:
        return await message.answer("Неверный формат даты! Используйте ДД.ММ.ГГГГ", reply_markup=kb.add_user_data)
    await state.update_data(data_edit=message.text)
    data_state = await state.get_data()
    surname, name, data = data_state['list_del'][data_state['edit_number']]
    await nt.update_date(message.from_user.id, surname, name, data_state['data_edit'])
    await message.answer('Данные изменены', reply_markup=kb.add_user_data)
    await state.clear()


@router.callback_query(F.data == 'cancel')
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Действие отменено", reply_markup=kb.add_user_data)
    await state.clear()
    await call.answer()


@router.callback_query(F.data == 'cancel_note')
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Действие отменено", reply_markup=kb.note_list)
    await state.clear()
    await call.answer()


@router.message(Form.first_name)
async def process_first_name(message: Message, state: FSMContext):
    if not validate_name(message.text):
        return await message.answer("Неверное имя! Используйте только буквы (мин. 2 символа).",
                                    reply_markup=kb.add_user_data)

    await state.update_data(first_name=message.text.title())
    await state.set_state(Form.last_name)
    await message.answer("Введите фамилию (только буквы):", reply_markup=kb.cancel_one)


@router.message(Form.last_name)
async def process_last_name(message: Message, state: FSMContext):
    if not validate_name(message.text):
        return await message.answer("Неверная фамилия! Используйте только буквы (мин. 2 символа).",
                                    reply_markup=kb.add_user_data)

    await state.update_data(last_name=message.text.title())
    await state.set_state(Form.birthday)
    await message.answer("Введите дату рождения (ДД.ММ.ГГГГ):", reply_markup=kb.cancel_one)


@router.message(Form.birthday)
async def add_user_reg(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.replace(",", "."), "%d.%m.%Y").date()
    except ValueError:
        return await message.answer("Неверный формат даты! Используйте ДД.ММ.ГГГГ", reply_markup=kb.add_user_data)

    await state.update_data(birthday=message.text)
    data_state = await state.get_data()
    if not await nt.get_birthday(data_state['last_name'], data_state['first_name']):
        await nt.add_birthday(message.from_user.id, data_state['last_name'], data_state['first_name'],
                              data_state['birthday'])
        await message.answer('Данные добавлены', reply_markup=kb.add_user_data)
    else:
        await message.answer('Такой запись уже есть', reply_markup=kb.add_user_data)
    await state.clear()


@router.message(F.text == '33')
async def file_open(message: Message):
    with open("DATA/33.txt", "r") as file:
        f = file.read()
        await message.answer(f"{f}")


@router.message(F.text.lower() == 'log')
async def file_open_logo(message: Message):
    with open("DATA/logs.log", "r") as file:
        f = file.read()[-3000:]
        await message.answer(f"{f}")
