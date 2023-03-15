from aiogram import Bot, Dispatcher, types
from config import TOKEN
import logging
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
import os.path
from search_db_profiles import *

logging.basicConfig(level=logging.INFO)
openai.api_key = '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'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
LOST_MESSAGE = ''
BUY_STATUS = 0


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
                         f"<b>💰 Баланс:</b> {money}\n"
                         f"<b>💎 Подписка:</b> {subscription}\n"
                         "\n"
                         "❓ Подробнее про токены /help", parse_mode="HTML")



@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("<b>Здравствуйте!</b> Вас приветствует Всемогущий-Бот. Я могу"
                         " ответить на любой интересующий вас вопрос. Вы можете спросить меня как текстом так и"
                         " голосом. Чтобы это сделать просто напиши мне. "
                         "Надеюсь я помогу вам! <b>В стандартной версии количество запросов ограниченно."
                         " Далее необходимо"
                         " преобрести подписку</b>"
                         " Это можно сделать по команде /buy.", parse_mode="HTML")
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
                    model='text-davinci-003', prompt=message.text, temperature=0.9, max_tokens=4000, top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.6,
                    stop=['You:']
                )
                update_token(message.from_user.id, len(message.text))
                await message.answer(response['choices'][0]['text'])
                LOST_MESSAGE = response["choices"][0]["text"]
                return
        try:
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
                model='text-davinci-003', prompt=result.text, temperature=0.9, max_tokens=1000, top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stop=['You:']
            )
            tts = gTTS(f'{response["choices"][0]["text"]}', lang='ru')
            tts.save(f'sound_ru{file_id}.mp3')
            tts_audio_file = open(f'sound_ru{file_id}.mp3', "rb")
            await bot.send_voice(message.from_user.id, tts_audio_file,
                                 reply_to_message_id=message.message_id)
            os.remove(file_on_disk)
            os.remove(f'tmp{file_id}.wav')
            os.remove(f'sound_ru{file_id}.mp3')

        except Exception:
            await message.answer("Что-то пошло не так. Повторите попытку позже")
            if os.path.exists(file_on_disk):
                os.remove(file_on_disk)
            if os.path.exists(f'tmp{file_id}.wav'):
                os.remove(f'tmp{file_id}.wav')
            if os.path.exists(f'sound_ru{file_id}.mp3'):
                os.remove(f'sound_ru{file_id}.mp3')



if __name__ == '__main__':
    executor.start_polling(dp)
