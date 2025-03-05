from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import app.datebase.requests as nt

import app.databases as db
import app.keyboards as kb

router_notes = Router()


class Notes(StatesGroup):
    fsm_note_name = State()
    fsm_note_text = State()
    note_number = State()
    note_list = State()
    note_all = State()
    note_delete = State()
    note_edit = State()
    name_text = State()
    note_new_add = State()
    new_text = State()
    add_text = State()


@router_notes.message(F.text == '📝Заметки')
async def note_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ты в меню добавления заметок.\nВыбери необходимое действие.", reply_markup=kb.note_list)


@router_notes.message(F.text == '📝Добавить заметку')
async def note_text(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Notes.fsm_note_name)
    await message.answer("Пишите название заметки 👇", reply_markup=kb.note_list)


@router_notes.message(Notes.fsm_note_name)
async def text_note(message: Message, state: FSMContext):
    await state.update_data(fsm_note_name=message.text)
    await state.set_state(Notes.fsm_note_text)
    await message.answer("Пишите текст заметки\nили отправьте фото, документ,\nаудио, видео с подписью 👇",
                         reply_markup=kb.note_list)


@router_notes.message(Notes.fsm_note_text)
async def save_note(message: Message, state: FSMContext):
    file_id, note_type = None, None
    if message.content_type == 'text':
        await state.update_data(fsm_note_text=message.text)
        data_state = await state.get_data()
        await nt.add_note(message.from_user.id, data_state['fsm_note_name'], data_state['fsm_note_text'],
                          note_type='text')
        await state.clear()
        return await message.answer("Заметка сохранена", reply_markup=kb.note_list)
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        note_type = 'photo'
    elif message.content_type == 'document':
        file_id = message.document.file_id
        note_type = 'document'
    elif message.content_type == 'voice':
        file_id = message.voice.file_id
        note_type = 'voice'
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
        note_type = 'audio'
    elif message.content_type == 'video':
        file_id = message.video.file_id
        note_type = 'video'
    caption_text = message.caption if message.caption else '----'
    await state.update_data(fsm_note_text=caption_text)
    data_state = await state.get_data()
    await nt.add_note(message.from_user.id, data_state['fsm_note_name'], data_state['fsm_note_text'],
                      note_type=note_type, file_id=file_id)
    await message.answer("Заметка сохранена", reply_markup=kb.note_list)
    await state.clear()


type_dict = {'text': '📝', 'photo': '🖼️', 'document': '📄', 'voice': '🎤', 'audio': '🎵', 'video': '🎞'}


@router_notes.message(F.text == '📋Мои заметки')
async def my_note_text(message: Message, state: FSMContext):
    await state.clear()
    notes_dict = await nt.note_view(message.from_user.id)
    if notes_dict:
        await state.update_data(note_list=notes_dict)
        in_kb = []
        for key, value in notes_dict.items():
            in_kb.append([InlineKeyboardButton(text=f'{type_dict[value[0]]}{value[1]}',
                                               callback_data=f'notes_{key}')])
        keyboard = InlineKeyboardMarkup(inline_keyboard=in_kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Ваши заметки", reply_markup=keyboard)
    else:
        await message.answer("У вас нет заметок",
                             reply_markup=kb.note_list)


@router_notes.callback_query(F.data.startswith('notes_'))
async def note_view(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_namber=call.data.split('_')[1])
    await state.set_state(Notes.note_all)
    data_state = await state.get_data()
    num = int(data_state['note_namber'])
    if data_state['note_list'][num][0] == 'photo':
        await call.message.answer_photo(data_state['note_list'][num][3], caption=f"{data_state['note_list'][num][1]}",
                                        reply_markup=kb.edit_note)
    elif data_state['note_list'][num][0] == 'document':
        await call.message.answer_document(data_state['note_list'][num][3],
                                           caption=f"{data_state['note_list'][num][1]}",
                                           reply_markup=kb.edit_note)
    elif data_state['note_list'][num][0] == 'voice':
        await call.message.answer_voice(data_state['note_list'][num][3],
                                        caption=f"{data_state['note_list'][num][1]}",
                                        reply_markup=kb.edit_note)
    elif data_state['note_list'][num][0] == 'audio':
        await call.message.answer_audio(data_state['note_list'][num][3],
                                        caption=f"{data_state['note_list'][num][1]}",
                                        reply_markup=kb.edit_note)
    elif data_state['note_list'][num][0] == 'video':
        await call.message.answer_video(data_state['note_list'][num][3],
                                        caption=f"{data_state['note_list'][num][1]}",
                                        reply_markup=kb.edit_note)
    elif data_state['note_list'][num][0] == 'text':
        await call.message.answer(f"{data_state['note_list'][num][2]}", reply_markup=kb.edit_note)
    await call.answer()


@router_notes.callback_query(Notes.note_all, F.data == 'note_edit')
async def edit_note(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_all=call.data)
    await state.set_state(Notes.note_edit)
    await call.message.answer("Имя заметки или текст заметки?", reply_markup=kb.note_edit)
    await call.answer()


@router_notes.callback_query(Notes.note_edit, F.data == 'edit_name')
async def edit_note_name(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_edit=call.data)
    await state.set_state(Notes.name_text)
    await call.message.answer("Пишите Имя заметки 👇", reply_markup=kb.note_list)
    await call.answer()


@router_notes.message(Notes.name_text)
async def save_note(message: Message, state: FSMContext):
    await state.update_data(name_text=message.text)
    data_state = await state.get_data()
    num = int(data_state['note_namber'])
    note_name = data_state['note_list'][num][1]
    note_text = data_state['note_list'][num][2]
    await nt.update_note_name(message.from_user.id, data_state['name_text'], note_name, note_text)
    await message.answer("Имя заметки сохранена", reply_markup=kb.note_list)
    await state.clear()


@router_notes.callback_query(Notes.note_edit, F.data == 'edit_text')
async def edit_note_text(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_edit=call.data)
    await state.set_state(Notes.note_new_add)
    await call.message.answer("Добавить к тексту или новый текст?", reply_markup=kb.note_edit_content)
    await call.answer()


@router_notes.callback_query(Notes.note_new_add, F.data == 'new_text')
async def note_new(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_edit_text=call.data)
    await state.set_state(Notes.new_text)
    await call.message.answer("Пишите новый текст заметки 👇", reply_markup=kb.note_list)
    await call.answer()


@router_notes.message(Notes.new_text)
async def note_new_text(message: Message, state: FSMContext):
    await state.update_data(new_text=message.text)
    data_state = await state.get_data()
    num = int(data_state['note_namber'])
    note_name = data_state['note_list'][num][1]
    note_text = data_state['note_list'][num][2]
    await nt.update_note_text(message.from_user.id, data_state['new_text'], note_name, note_text)
    await message.answer("Новый текст сохранена", reply_markup=kb.note_list)
    await state.clear()


@router_notes.callback_query(Notes.note_new_add, F.data == 'add_text')
async def note_add(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_edit_text=call.data)
    await state.set_state(Notes.add_text)
    await call.message.answer("Пишите текст для добавления к заметке 👇", reply_markup=kb.note_list)
    await call.answer()


@router_notes.message(Notes.add_text)
async def note_add_text(message: Message, state: FSMContext):
    await state.update_data(add_text=message.text)
    data_state = await state.get_data()
    num = int(data_state['note_namber'])
    note_name = data_state['note_list'][num][1]
    note_text = data_state['note_list'][num][2]
    if note_text == '----':
        all_text = f"{data_state['add_text']}"
    else:
        all_text = f"{note_text}\n----\n{data_state['add_text']}"
    await nt.update_note_text(message.from_user.id, all_text, note_name, note_text)
    await message.answer("Текст добавлен к заметке", reply_markup=kb.note_list)
    await state.clear()


@router_notes.callback_query(Notes.note_all, F.data == 'note_delete')
async def delete_note(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_all=call.data)
    await state.set_state(Notes.note_delete)
    data_state = await state.get_data()
    num = int(data_state['note_namber'])
    await call.message.answer(f"{type_dict[data_state['note_list'][num][2]]}{data_state['note_list'][num][0]}",
                              reply_markup=kb.note_delete)
    await call.answer()


@router_notes.callback_query(Notes.note_delete, F.data == 'delete_note')
async def delete_note_es(call: CallbackQuery, state: FSMContext):
    await state.update_data(note_delete=call.data)
    data_state = await state.get_data()
    num = int(data_state['note_namber'])
    await db.note_delete(call.from_user.id, data_state['note_list'][num][0], data_state['note_list'][num][1])
    await call.message.answer("Заметка удалена!!!", reply_markup=kb.note_list)
    await call.answer()
    await state.clear()


@router_notes.callback_query(F.data == 'delete')
async def delete_user(call: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    await db.delete_to_number(call.from_user.id, int(data_state['del_number']))
    await call.message.answer('Данные удалены', reply_markup=kb.note_list)
    await state.clear()
    await call.answer()


@router_notes.callback_query(F.data == 'cancel')
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Действие отменено", reply_markup=kb.add_user_data)
    await state.clear()
    await call.answer()


@router_notes.callback_query(F.data == 'cancel_note')
async def cancel_note(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Действие отменено", reply_markup=kb.note_list)
    await state.clear()
    await call.answer()


@router_notes.callback_query()
async def note_callback(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Начните заново", reply_markup=kb.note_list)
    await state.clear()
    await call.answer()
