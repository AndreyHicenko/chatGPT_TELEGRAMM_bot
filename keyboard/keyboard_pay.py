from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

btn_replenish = InlineKeyboardButton(text='Пополнить баланс', callback_data='top_up')
btn_subscription = InlineKeyboardButton(text='Преобрести подписку', callback_data='buy_subscription')
top_up_menu = InlineKeyboardMarkup(row_width=1)
top_up_menu.insert(btn_replenish)
top_up_menu.insert(btn_subscription)

top_up_menu_2 = InlineKeyboardMarkup(row_width=1)
top_up_menu_2.insert(btn_replenish)



btn_100r = InlineKeyboardButton(text='100', callback_data='100_rub')
money_auth_menu = InlineKeyboardMarkup(row_width=3)
money_auth_menu.add(btn_100r)


