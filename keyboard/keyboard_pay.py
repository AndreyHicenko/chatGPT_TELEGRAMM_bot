from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

btn_replenish = InlineKeyboardButton(text='Пополнить баланс', callback_data='top_up')
top_up_menu = InlineKeyboardMarkup(row_width=1)
top_up_menu.insert(btn_replenish)