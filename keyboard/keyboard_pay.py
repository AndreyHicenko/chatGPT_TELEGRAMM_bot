from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

button_1month = KeyboardButton('Подписка на 1 месяц')
button_6month = KeyboardButton('Подписка на 6 месяцев')
button_12month = KeyboardButton('Подписка на год')
button_forever = KeyboardButton('Подписка навсегда')

pay_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True)
pay_kb.add(button_1month)
pay_kb.add(button_6month)
pay_kb.add(button_12month)
pay_kb.add(button_forever)