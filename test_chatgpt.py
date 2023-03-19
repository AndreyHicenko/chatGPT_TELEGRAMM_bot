from aiogram import Bot, Dispatcher, types

from config import TOKEN, TOKEN_YOOMONEY
import logging
import config
from aiogram.utils import executor
from pathlib import Path
import openai

import time
import sys
import os
from googletrans import Translator
from moviepy.editor import concatenate_audioclips, AudioFileClip
from gtts import gTTS
from aiogram.types.message import ContentType
from search_db import *
from yoomoney import Quickpay
from yoomoney import Client
import os.path
from keyboard.keyboard_pay import *
import random
import string

logging.basicConfig(level=logging.INFO)
OPENAI_API = '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'
openai.api_key = OPENAI_API
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
LOST_MESSAGE = ''
BUY_STATUS = 0
T = 0


@dp.callback_query_handler(text='top_up')
async def top_up(callback: types.callback_query):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id, "Выберете сумму для пополнения", reply_markup=money_auth_menu)

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer("🔹 Токены нужны чтобы задавать вопросы боту в бесплатной версии.  \n \n"
                         "🔹 Они тратятся в соотношении 6 токенов ~ 1 символ любого алфавита. \n \n"
                         "🔹 Если у вас есть "
                         "подписка то токены не ограничены\n \n"
                         "🔹 Если токены кончиличь необходимо преобрести подписку.", parse_mode="HTML")



# доделать оплату
@dp.callback_query_handler(text='100_rub')
async def pop_bol100_callback(callback: types.callback_query):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    latters_and_strings = string.ascii_lowercase + string.digits
    label = ''.join(random.sample(latters_and_strings, 10))
    quickpay = Quickpay(
        receiver="4100118147874677",
        quickpay_form="shop",
        targets="Sponsor this project",
        paymentType="SB",
        sum=100, label=label
    )
    update_label(label, callback.from_user.id)
    url = quickpay.redirected_url
    btn_popolnit100_balance = InlineKeyboardButton(text='Оплатить', callback_data='pop_bol100_menu', url=url)
    btn_check = InlineKeyboardButton(text='Проверить оплату', callback_data='check_paymant')
    pop_bol100_menu = InlineKeyboardMarkup(row_width=1)
    pop_bol100_menu.insert(btn_popolnit100_balance)
    pop_bol100_menu.insert(btn_check)

    await bot.send_message(callback.from_user.id, "💵 <b>Пополнение баланса на сумму</b> 100₽"
                                                  "\n \n"
                                                  "📌 <b>Инструкция по оплате:</b>"
                                                  "\n \n"
                                                  "1. Нажмите кнопку «Оплатить» и перейдите на сайт"
                                                  "\n"
                                                  "2. На странице введите данные и оплатите"
                                                  "\n"
                                                  "3. После оплаты нажмите кнопку «<b>Проверить оплату</b>»"
                                                  "\n",
                           parse_mode="HTML",
                           reply_markup=pop_bol100_menu)

@dp.callback_query_handler(text='buy_subscription')
async def buy_subscription(callback: types.callback_query):
    if not upddate_datebase(callback.from_user.id, 1):
        await bot.send_message(callback.from_user.id, '❌ На балансе недостаточно средст \n \n'
                                                      ' Для пополнения баланса нажмите кнопку «Пополнить баланс»',
                               reply_markup=top_up_menu_2)
    elif upddate_datebase(callback.from_user.id, 1):
        await bot.send_message(callback.from_user.id, upddate_datebase(callback.from_user.id, 1))

@dp.callback_query_handler(text='check_paymant')
async def check_pay(callback: types.callback_query):
    data = get_payment_status(callback.from_user.id)
    status = data[0][0]
    label = data[0][1]
    if status == 0:
        client = Client(TOKEN_YOOMONEY)
        history = client.operation_history(label=label)
        try:
            operation = history.operations[-1]
            if operation.status == 'success':
                await bot.delete_message(callback.from_user.id, callback.message.message_id)
                update_payment_status(callback.from_user.id)
                update_money(callback.from_user.id, 100)
                await bot.send_message(callback.from_user.id, 'Счет успешно пополнен на 100₽')
                update_payment_status_false(callback.from_user.id)

        except Exception as e:
            await bot.send_message(callback.from_user.id, '❌ Оплата не обнаружена!')
    else:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        update_money(callback.from_user.id, 100)
        await bot.send_message(callback.from_user.id, 'Счет успешно пополнен на 100₽')
        update_payment_status_false(callback.from_user.id)


@dp.message_handler(commands=['agreement'])
async def users_agreement(message: types.Message):
    await message.answer("❗ Во время использования бота <b>запрешается</b> спамить,"
                         " задавать вопросы на политические темы, "
                         "выражать отношение к другим народам", parse_mode="HTML")


@dp.message_handler(commands=['profile'])
async def profile_start(message: types.Message):
    money = search_money(message.from_user.id)
    subscription = search_subscription_availability(message.from_user.id)
    if subscription == 0:
        subscription = 'Неактивна'
    elif subscription == 1:
        subscription = 'Активна'
    tokens_with_user = search_token(message.from_user.id)
    await message.answer("<b>📓 Ваш профиль</b>"
                         "\n \n"
                         f"<b>👤 Имя:</b> {message.from_user.first_name} {message.from_user.last_name} \n"
                         f"<b>🔑 Токенов осталось:</b> {tokens_with_user}\n"
                         f"<b>💰 Баланс:</b> {money}₽\n"
                         f"<b>💎 Подписка:</b> {subscription}\n"
                         "\n"
                         "❓ Подробнее про токены /help", parse_mode="HTML", reply_markup=top_up_menu)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("<b>Здравствуйте!</b> Вас приветствует Всемогущий-Бот. Я могу"
                         " ответить на любой интересующий вас вопрос. Вы можете спросить меня как текстом так и"
                         " голосом. Чтобы это сделать просто напиши мне. "
                         "Надеюсь я помогу вам! <b>В стандартной версии количество запросов ограниченно."
                         " Далее необходимо"
                         " преобрести подписку</b>"
                         " Это можно сделать в панели /profile."
                         "Перед использованием <b>прочитайте правила использования</b>, представленное во вкладке"
                         " /agreement", parse_mode="HTML")
    if search_user_with_db(message.from_user.id):
        pass
    elif not search_user_with_db(message.from_user.id):
        add_new_user(message.from_user.id)


# для голоса обязательно
@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
]
)
@dp.message_handler()
async def send_message(message: types.Message):
    global LOST_MESSAGE, BUY_STATUS, T
    if datetime.datetime.strptime(str(datetime.datetime.now().date()), '%Y-%m-%d')\
            > datetime.datetime.strptime(date_check(message.from_user.id)[0][0], '%Y-%m-%d'):
        await message.answer('❗ Действие подписки окончено')
        update_subscription_availability_false(message.from_user.id)
    if search_token(message.from_user.id) == 0 and search_subscription_availability(message.from_user.id) == 0:
        await message.answer("❗ <b>Количиство бесплатных токенов исчерпано</b>, чтобы продолжить"
                             " использовать бота <b>преобретите подписку</b> Чтобы это сделать перейдите во вкладку "
                             "/profile", parse_mode="HTML")
    # if not serch_user(message.from_user.id):
    #     await message.answer("Пожалуйста, преобретите подписку")
    elif int(search_token(message.from_user.id)) > 0 or search_subscription_availability(message.from_user.id) == 1:
        if message.content_type == types.ContentType.VOICE:
            file_id = message.voice.file_id
        elif message.content_type == types.ContentType.AUDIO:
            file_id = message.audio.file_id
        elif message.content_type == types.ContentType.DOCUMENT:
            file_id = message.document.file_id
        elif T == 1:
            pass
        else:

            try:
                x = ['⏳ Чтобы отправить следующее сообщение ожидайте 14 сек']
                if message.text not in x:
                    if message.text[-1] not in string.punctuation:
                        message.text = message.text + '.'
                    response = openai.Completion.create(
                        model='text-davinci-003', prompt=message.text, temperature=0.2, max_tokens=4000, top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.6,
                        stop=['You:']
                    )
                    if search_subscription_availability(message.from_user.id) == 0:
                        update_token(message.from_user.id, len(message.text))
                    await message.answer(response['choices'][0]['text'])
                    LOST_MESSAGE = response["choices"][0]["text"]
                    # таймер между сообщениями
                    T = 1
                    time.sleep(1)
                    msg = await message.answer('⏳ Чтобы отправить следующее сообщение ожидайте 14 сек')
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 13 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 12 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 11 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 10 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 9 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 8 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 7 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 6 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 5 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 4 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 3 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 2 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 1 сек")
                    time.sleep(1)
                    await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 0 сек")
                    time.sleep(1)
                    await msg.edit_text(f"Вы можете отправить сообщение")
                    T = 0
                    return

            except Exception:
                await message.answer('<b>❗ Произошла ошибка</b>, возможно вопрос или ответ на ваш запрос привышает'
                                     ' допустимое значение длины', parse_mode="HTML")
                return
        try:
            if T == 1:
                pass
            elif T == 0:
                file = await bot.get_file(file_id)
                file_path = file.file_path
                file_on_disk = Path("", f"{file_id}.wav")
                await bot.download_file(file_path, destination=f'{file_id}.wav')
                audio_clip_paths = ['123.wav', f'{file_id}.wav']
                clips = [AudioFileClip(c) for c in audio_clip_paths]
                final_clip = concatenate_audioclips(clips)
                final_clip.write_audiofile(f'tmp{file_id}.wav')
                audio_file = open(f'tmp{file_id}.wav', "rb")
                transcript = openai.Audio.translate("whisper-1", audio_file)
                translator = Translator()
                audio_file.close()
                result = translator.translate(transcript["text"], src='en', dest='ru')
                response = openai.Completion.create(
                    model='text-davinci-003', prompt=result.text, temperature=0.2, max_tokens=1000, top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.6,
                    stop=['You:']
                )
                if search_subscription_availability(message.from_user.id) == 0:
                    update_token(message.from_user.id, len(result.text))
                tts = gTTS(f'{response["choices"][0]["text"]}', lang='ru')
                tts.save(f'sound_ru{file_id}.mp3')
                tts_audio_file = open(f'sound_ru{file_id}.mp3', "rb")
                await bot.send_voice(message.from_user.id, tts_audio_file,
                                     reply_to_message_id=message.message_id)
                os.remove(file_on_disk)
                os.remove(f'tmp{file_id}.wav')
                os.remove(f'sound_ru{file_id}.mp3')

        except Exception:
            await message.answer("<b>❗ Что-то пошло не так</b>. Повторите попытку позже", parse_mode="HTML")
            if os.path.exists(file_on_disk):
                os.remove(file_on_disk)
            if os.path.exists(f'tmp{file_id}.wav'):
                os.remove(f'tmp{file_id}.wav')
                audio_file.close()
            if os.path.exists(f'sound_ru{file_id}.mp3'):
                os.remove(f'sound_ru{file_id}.mp3')
                # таймер между сообщениями
            T = 1
            time.sleep(1)
            msg = await message.answer('⏳ Чтобы отправить следующее сообщение ожидайте 14 сек')
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 13 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 12 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 11 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 10 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 9 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 8 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 7 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 6 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 5 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 4 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 3 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 2 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 1 сек")
            time.sleep(1)
            await msg.edit_text(f"⏳ Чтобы отправить следующее сообщение ожидайте 0 сек")
            time.sleep(1)
            await msg.edit_text(f"Вы можете отправить сообщение")
            T = 0


if __name__ == '__main__':
    executor.start_polling(dp)
