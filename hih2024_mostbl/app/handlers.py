import io

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import os

import app.keyboards as kb

import dushko

router = Router()

class Editing(StatesGroup):
    fds = State()
    tw = State()
    tf = State()
    lkmc = State()


def write_numbers_to_file(filename, numbers):
    with open(filename, 'w') as file:
        for number in numbers:
            file.write(f"{number}\n")


def read_numbers_from_file(filename):
    numbers = []
    with open(filename, 'r') as file:
        for line in file:
            numbers.append(float(line.strip()))  # Используйте int() если хотите целые числа
    return numbers


"""
router.message(content_types = ['photo'])
async def take_photo(message: type.Message):
    photo = message.photo
    await photo.download()
"""


@router.message(F.photo)
async def get_photo(message: Message):
    print(11111111)
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    down_file = await message.bot.download_file(file_path=file.file_path)
    with open (r'C:\Users\79117\PycharmProjects\HIH2024_car_recogn/test.png', 'wb') as new_file:
        new_file.write(down_file.getbuffer().tobytes())
    await message.answer('Фото принято, идет обработка!')
    numbers = read_numbers_from_file('paint_params')
    area, angle = dushko.dushko_recogn(float(numbers[0]))
    photo_file = FSInputFile(r'C:\Users\79117\PycharmProjects\HIH2024_car_recogn\result.jpg')
    await message.answer_photo(photo=photo_file, caption=f'Площадь переднего крыла: {round(area,2)}м^2')
    photo_file = FSInputFile(r'C:\Users\79117\PycharmProjects\HIH2024_car_recogn\fig1.png')
    await message.answer_photo(photo=photo_file, caption=f'Угол: 0')
    photo_file = FSInputFile(r'C:\Users\79117\PycharmProjects\HIH2024_car_recogn\fig2.png')
    await message.answer_photo(photo=photo_file, caption=f'Лучший угол: {angle}')



@router.message(Command('send_photo'))
async def cmd_start(message: Message, state: FSMContext):
    photo_file = FSInputFile('C:/Users/79117/Pictures/Снимок экрана 2023-06-27 223639.png')
    await message.answer_photo(photo=photo_file, caption='Моя <u>отформатированная</u> подпись к <b>фото</b>')



@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer('Приветствуем!', reply_markup=kb.main)
#    numbers = read_numbers_from_file('paint_params')
    await state.update_data(fds='0')
    await state.update_data(wide='0')
    await state.update_data(flash='0')
    await state.update_data(cost='0')


@router.message(F.text == 'Menu')
async def cmd_start(message: Message):
    await message.answer('Основное меню выведено на экран', reply_markup=kb.main)


@router.message(F.text == 'Обработать фотографию')
async def edit_menu(message: Message):
    await message.answer('Пришлите изображение:')


@router.message(F.text == 'Изменить параметры')
async def edit_menu(message: Message):
    await message.answer('Выберите параметр для редактирования:', reply_markup=kb.catalog)


@router.message(F.text == 'Нынешние параметры')
async def edit_menu(message: Message, state: FSMContext):
    numbers = read_numbers_from_file('paint_params')
    await message.answer(f'Площадь двери: {numbers[0]}м\nШирина факела: {numbers[1]}м'
                         f'\nВылет факела: {numbers[2]}м\nСтоимость 1л ЛКМ: {numbers[3]}р/л')


# ответы на кнопки редактирования
@router.callback_query(F.data == 'door_square')
async def edit_fds_q(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Editing.fds)
    await callback.answer('Нынешнее значение: '+str(read_numbers_from_file('paint_params')[0]))
    await callback.message.answer('Введите площадь в м^2')


@router.callback_query(F.data == 'torch_wide')
async def edit_fds_q(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Editing.tw)
    await callback.answer('Нынешнее значение: '+str(read_numbers_from_file('paint_params')[1]))
    await callback.message.answer('Введите ширину в м')


@router.callback_query(F.data == 'torch_flash')
async def edit_fds_q(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Editing.tf)
    await callback.answer('Нынешнее значение: '+str(read_numbers_from_file('paint_params')[2]))
    await callback.message.answer('Введите вылет в м')


@router.callback_query(F.data == 'LKM_cost')
async def edit_fds_q(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Editing.lkmc)
    await callback.answer(f'Нынешнее значение: '+str(read_numbers_from_file('paint_params')[3]))
    await callback.message.answer('Введите стоимость в рублях')


# принятие изменений
@router.message(Editing.fds)
async def edit_fds_e(message: Message, state: FSMContext):
    await state.update_data(fds=message.text.replace(',', '.'))
    data = await state.get_data()
    numbers = read_numbers_from_file('paint_params')
    numbers[0] = float(data["fds"])
    write_numbers_to_file('paint_params',numbers)
    await message.answer(f'Новая площадь: {data["fds"]}м')


@router.message(Editing.tw)
async def edit_fds_e(message: Message, state: FSMContext):
    await state.update_data(wide=message.text.replace(',', '.'))
    data = await state.get_data()
    numbers = read_numbers_from_file('paint_params')
    numbers[1] = float(data["wide"])
    write_numbers_to_file('paint_params',numbers)
    await message.answer(f'Новая ширина: {data["wide"]}м')


@router.message(Editing.tf)
async def edit_fds_e(message: Message, state: FSMContext):
    await state.update_data(flash=message.text.replace(',', '.'))
    data = await state.get_data()
    numbers = read_numbers_from_file('paint_params')
    numbers[2] = float(data["flash"])
    write_numbers_to_file('paint_params',numbers)
    await message.answer(f'Новый вылет: {data["flash"]}м')



@router.message(Editing.lkmc)
async def edit_fds_e(message: Message, state: FSMContext):
    await state.update_data(cost=message.text.replace(',', '.'))
    data = await state.get_data()
    numbers = read_numbers_from_file('paint_params')
    numbers[3] = float(data["cost"])
    write_numbers_to_file('paint_params',numbers)
    await message.answer(f'Новая стоимость: {data["cost"]}р/л')
