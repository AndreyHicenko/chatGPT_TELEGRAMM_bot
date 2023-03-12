from aiogram import Bot, Dispatcher, types
from config import TOKEN
import config
from aiogram.utils import executor
from pathlib import Path
import openai
import os
from googletrans import Translator
from moviepy.editor import concatenate_audioclips, AudioFileClip
from gtts import gTTS
from aiogram.types.message import ContentType
from search_db import *

openai.api_key = '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'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
LOST_MESSAGE = ''
BUY_STATUS = 0

# оплата прайс
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=500 * 100)  # в копейках (руб)


# buy
@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):
    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Подписка на бота",
                           description="Подписки на 1 месяц",
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")



# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    global BUY_STATUS
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")
    serch_user_in_db(message.from_user.id, 1)
    await message.answer('Теперь вы можете спросить меня')


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! Вас приветствует Всемогущий-Бот. Я могу"
                         " ответить на любой интересующий вас вопрос. Вы можете спросить меня как текстом так и"
                         " голосом. Чтобы это сделать просто напиши мне. "
                         "Надеюсь я помогу вам! Чтобы использовать меня необходимо преобрести подписку."
                         " Это можно сделать по команде /buy")


# для голоса обязательно
@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
]
)
@dp.message_handler()
async def send_message(message: types.Message):
    global LOST_MESSAGE, BUY_STATUS
    if not serch_user(message.from_user.id):
        await message.answer("Пожалуйста, преобретите подписку")
    elif serch_user(message.from_user.id):
        if message.content_type == types.ContentType.VOICE:
            file_id = message.voice.file_id
        elif message.content_type == types.ContentType.AUDIO:
            file_id = message.audio.file_id
        elif message.content_type == types.ContentType.DOCUMENT:
            file_id = message.document.file_id
        else:
            if message.text.lower() == 'продолжи':
                response = openai.Completion.create(
                    model='text-davinci-003', prompt='Продолжи' + ' ' + LOST_MESSAGE,
                    temperature=0.9, max_tokens=1000, top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.6,
                    stop=['You:']
                )
                await message.answer(response['choices'][0]['text'])
                return
            else:
                response = openai.Completion.create(
                    model='text-davinci-003', prompt=message.text, temperature=0.9, max_tokens=1000, top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.6,
                    stop=['You:']
                )
                await message.answer(response['choices'][0]['text'])
                LOST_MESSAGE = response["choices"][0]["text"]
                return
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_on_disk = Path("", f"{file_id}.wav")
        await bot.download_file(file_path, destination=f'{file_id}.wav')
        audio_clip_paths = ['123.wav', f'{file_id}.wav']
        clips = [AudioFileClip(c) for c in audio_clip_paths]
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile('tmp.wav')
        audio_file = open(f'tmp.wav', "rb")
        transcript = openai.Audio.translate("whisper-1", audio_file)
        translator = Translator()
        result = translator.translate(transcript["text"], src='en', dest='ru')
        response = openai.Completion.create(
            model='text-davinci-003', prompt=result.text, temperature=0.9, max_tokens=1000, top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=['You:']
        )
        tts = gTTS(f'{response["choices"][0]["text"]}', lang='ru')
        tts.save('sound_ru.mp3')
        tts_audio_file = open(f'sound_ru.mp3', "rb")
        await bot.send_voice(message.from_user.id, tts_audio_file,
                             reply_to_message_id=message.message_id)
        os.remove(file_on_disk)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
