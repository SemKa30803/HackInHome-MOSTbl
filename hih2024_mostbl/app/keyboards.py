from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Обработать фотографию')],
                                     [KeyboardButton(text='Нынешние параметры')],
                                     [KeyboardButton(text='Изменить параметры')]],
                           resize_keyboard=True)

catalog = InlineKeyboardMarkup(inline_keyboard=
                               [[InlineKeyboardButton(text='Физическая площадь передней двери, м^2', callback_data='door_square')],
                                [InlineKeyboardButton(text='Ширина факела', callback_data='torch_wide')],
                                [InlineKeyboardButton(text='Вылет факела', callback_data='torch_flash')],
                                [InlineKeyboardButton(text='Стоимость 1л ЛКМ', callback_data='LKM_cost')]])

