from aiogram import Bot, F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import MY_ID
import os

import app.datebase.requests_admin as ad

router_admin = Router()


class Reg(StatesGroup):
    del_id = State()
    text_1 = State()
    del_user = State()


class PhotoForm(StatesGroup):
    waiting_for_photo = State()  # Шаг 1: Ожидание фото
    waiting_for_caption = State()  # Шаг 2: Ожидание подписи


@router_admin.message(F.text == 'Удалить данные')
async def delete_user(message: Message, state: FSMContext):
    await state.set_state(Reg.del_user)
    await message.answer('Введите Ф.И.\nПример: Иванов Иван')


@router_admin.message(Reg.del_user)
async def delete_user_reg(message: Message, state: FSMContext):
    await state.update_data(del_user=message.text)
    data_state = await state.get_data()
    data_list = data_state['del_user'].split()
    await ad.admin_delete(data_list[0], data_list[1])
    await message.answer('Данные удалены')
    await state.clear()


# Старт процесса
@router_admin.message(F.text == "Картинка", F.from_user.id == MY_ID)
async def start_photo_upload(message: Message, state: FSMContext):
    await message.answer("📷 Отправьте фото, к которому нужно добавить подпись")
    await state.set_state(PhotoForm.waiting_for_photo)


# Обработка фото
@router_admin.message(PhotoForm.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    # Сохраняем фото
    photo = message.photo[-1]
    await state.update_data(photo_id=photo.file_id)
    # Переходим к ожиданию подписи
    await state.set_state(PhotoForm.waiting_for_caption)
    await message.answer("✅ Фото принято! Теперь введите подпись к фото")


# Обработка подписи
@router_admin.message(PhotoForm.waiting_for_caption, F.text)
async def process_caption(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(caption=message.text)
    full_data = await state.get_data()
    for tg_id, name, data in await ad.db_select_id():
        try:
            await bot.send_photo(int(tg_id), full_data['photo_id'],
                                 caption=f"Привет {name}!\n{full_data['caption']}\nАдминистрация!!!")
        except Exception as e:
            await bot.send_message(MY_ID, f'Ошибка при отправке сообщения пользователю {tg_id}: {e}')
    await state.clear()


@router_admin.message(F.text == "Объявление")
async def cmd_admin_ad(message: Message, state: FSMContext):
    await state.set_state(Reg.text_1)
    await message.answer("Пишите объявление")


@router_admin.message(Reg.text_1)
async def reg_admin_text_1(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text_1=message.text)
    data_state = await state.get_data()
    for tg_id, name, data in await ad.db_select_id():
        try:
            await bot.send_message(int(tg_id), f"Привет {name}!\n{data_state['text_1']}\nАдминистрация!!!")
        except Exception as e:
            await bot.send_message(MY_ID, f'Ошибка при отправке сообщения пользователю {tg_id}: {e}')
    await state.clear()


@router_admin.message(F.photo, F.from_user.id == MY_ID)
async def cmd_admin_photo(message: Message, bot: Bot):
    file_name = f"images/{len(os.listdir('images')) + 1}.jpg"
    await bot.download(message.photo[-1], destination=file_name)
    await message.answer('Фото сохранено')


@router_admin.message(F.text == 'Данные по ID')
async def viev_id(message: Message, state: FSMContext):
    data_txt = ""
    for tg_id, name, data in await ad.db_select_id():
        data_txt += f"{tg_id} {name} {data}\n"
    await message.answer(f"{data_txt}")
    await state.clear()


@router_admin.message(F.text == '🗑️Удалить по ID')
async def delete_id(message: Message, state: FSMContext):
    await state.set_state(Reg.del_id)
    await message.answer('Введите ID')


@router_admin.message(Reg.del_id)
async def delete_id_reg(message: Message, state: FSMContext):
    await state.update_data(del_id=message.text)
    data_state = await state.get_data()
    await ad.db_delete_id(data_state['del_id'])
    await message.answer('Данные по ID удалены')
    await state.clear()


@router_admin.message()
async def echo(message: Message):
    await message.reply('ошибка!')
