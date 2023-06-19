from config import *
import logging
from keyboard import *
from worker import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, InputFile
from aiogram.dispatcher.filters import Command, Text
from aiogram import Bot, Dispatcher, executor, types
import psycopg2
import openai
import json
import mysql.connector
from base64 import b64decode
import schedule
import asyncio
import time
from random import randint,choice
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload



logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

openai.api_key = OpenAITOKEN # init open ai api token

# chat gpt
def gptFunc(message, user):
    array = flags[str(user)]['history'] # get history
    array.append(message)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",

            messages=[
                {"role": "user", "content": "\n".join(array)}
            ],
            max_tokens=1024,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )




    except: pass
    # return data to user

    reply = response.choices[0].message.content
    array.append(reply)

    return reply

# generation image function - you must improve it - update promt for providing better results
def generationFunc(message, name): # message - prompt, name - tg_id(only use for create name of file)
    image_response = openai.Image.create(
            prompt=message + ".нужен только эскиз тату, только просто рисунок без частей тела.", # prompt + settings
            n=1,
            size='512x512',
            response_format='b64_json'
        )

    with open(name + '.json', "w") as file: # get image data to json
        json.dump(image_response, file, indent=4, ensure_ascii=False)

    image_data = b64decode(image_response['data'][0]['b64_json']) # get image data
    file_name = name + ".png"

    with open(file_name, 'wb') as file: # put image to file
        file.write(image_data)

# data base config
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=name
)

async def download_photos_from_drive(user_id):
    drive_service = build('drive', 'v3', developerKey=google_ip_key)
    results = drive_service.files().list(q=f"'{FOLDER_ID}' in parents and trashed=false").execute()
    items = results.get('files', [])

    if not items:
        print('Поражение, фотки не найдены')
        await bot.send_message(user_id,"При загрузке фотографий возникла ошибка")
        return

    for item in items:
        file_id = item['id']
        file_name = item['name']
        destination = os.path.join(DESTINATION_FOLDER, file_name)
        request = drive_service.files().get_media(fileId=file_id)

        with io.FileIO(destination, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()


        print(f' Победа, файл "{file_name}" успешно загружен.')
    await bot.send_message(user_id, "Все фотографии успешно загружены")
async def delete_photos(chat_id):
    photos_folder = os.path.join(DESTINATION_FOLDER)

    if not os.path.exists(photos_folder):
        print('Папка photos не существует')
        return

    for file_name in os.listdir(photos_folder):
        file_path = os.path.join(photos_folder, file_name)
        os.remove(file_path)
        print(f'Файл "{file_name}" удален.')

    print('Все фотографии удалены.')
    await bot.send_message(chat_id, "Все фотографии успешно удалены")

sent_photos = {}
async def send_random_photo(chat_id, sent_photos):
    photos_folder = os.path.join(DESTINATION_FOLDER)

    if not os.path.exists(photos_folder):
        print('Папка "photos" не существует.')
        return

    photos = [file_name for file_name in os.listdir(photos_folder) if file_name not in sent_photos.get(chat_id, [])]

    if not photos:
        print('Все фотографии уже отправлены.')
        await bot.send_message(chat_id, "На сегодня это все эскизы, но скоро будут новые")


        return

    random_photo = choice(photos)
    file_path = os.path.join(photos_folder, random_photo)

    with open(file_path, 'rb') as photo:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Еще эскиз", callback_data="art"))
        await bot.send_photo(chat_id, photo,reply_markup=keyboard)

    sent_photos.setdefault(chat_id, []).append(random_photo)
    print(f'Фотография "{random_photo}" отправлена.')

connection.autocommit = True # make autocommit


# create dict for flags
with open('data.json', 'r') as file:
    # Загрузка данных из файла в словарь
    flags = json.load(file)
 # this dictionary its only for shot time data, this is consist only flags and array of dialog
# structure of dictionary: telegram_id: {assistent: , generate: ,array: []}
def dumpData(data):
    with open('data.json', 'w') as file:
        json.dump(data, file)

# db functions
# add company
def addCompany(name):
    try:
        with connection.cursor() as cursor:
            requestToDB = """INSERT INTO Companies (company) VALUES (%s)""" # insert data to db
            companyData = (name) # data to db
            cursor.execute(requestToDB, companyData) # make request

    except Exception as err:
        pass

# add user
def addUser(telegram_ad, name, company):
    try:
        with connection.cursor() as cursor:
            requestToDB = """INSERT INTO Users (telega, name, company, messages, images) VALUES (%s, %s, %s, %s, %s)""" # its add new user to db
            companyData = (int(telegram_ad), name, company, 0, 0) # insert data
            cursor.execute(requestToDB, companyData) # make request


    except Exception as err:
        print(err)

# show companies
def showCompanies():
    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM companies" # show list of all companies
            cursor.execute(select_query) # make request to db
            companies_data = cursor.fetchall() # return all data from db
            return companies_data
    except Exception as err:
        return err

# update messages
def updateCountMessages(id):
    try:
        with connection.cursor() as cursor:
            query = """UPDATE users SET messages=messages+1 WHERE telega = (%s)""" # update count of messages, idk why its no working
            dd = (id,)
            cursor.execute(query, dd)
            print("HELLO")

    except: pass

def updateCountImages(id):
    try:
        with connection.cursor() as cursor:
            query = """UPDATE users SET images=images+1 WHERE telega = (%s)""" # update count of images, idk why its no working
            dd = (id,)
            cursor.execute(query, dd)

    except: pass

# show users
def showUsers():
    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM users" # sql - show all data in database
            cursor.execute(select_query) # make request to db
            users_data = cursor.fetchall() # return all data from db
            return users_data # return data to python
    except Exception as err:
        return err

def updateLimit():
    try:
        with connection.cursor() as cursor:
            q = """UPDATE users SET messages = 0, images = 0"""
            cursor.execute(q)
    except: pass



def checkLimitM(id):
    try:
        with connection.cursor() as cursor:
            q = """SELECT messages FROM users WHERE telega=(%s)"""
            cursor.execute(q, (id,))
            return cursor.fetchone()
    except: pass

def checkLimitI(id):
    try:
        with connection.cursor() as cursor:
            q = """SELECT images FROM users WHERE telega=(%s)"""
            cursor.execute(q, (id,))
            return cursor.fetchone()
    except: pass


# end db functions


# start function - need to input token
@dp.message_handler(commands=["start"])
async def start(message:types.Message):
    addUser(int(message.from_user.id), message.from_user.username, 'konura') #add user to data base
    flags[str(message.from_user.id)] = {'assistent': False, 'generate': False, 'history': ["Ты тату-мастер, помогающий людям в ответах на их вопросы касталеьно татуировок, будь более человекоподобным в диалоге, а также игнорируй вопросы, не касающиеся татуировок или пирсинга, отвечай максимально коротко"]} # here i make flags with dictionary and also make setting for chat gpt role
    dumpData(flags)
    await message.answer(f"Привет, {message.from_user.first_name} ! Я чат-бот от студии Конура на основе  передовых нейросетей от Open AI.  Моя задача - помочь тебе с вопросами о татуировке. Я могу дать полезные советы, помочь с эскизом, рассказать о студии  и организовать встречу с нашими татуировщиками. С чего бы ты хотел начать?", reply_markup=telegramKeyboard)
    if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664) or (message.from_user.id == 787863728):
        await message.answer("/check_all_user - список всех пользователей бота \n/refresh_sketches - обновление фотографий с гугл диска \n/photo - загрузка фото для рассылки \n/button_text - загрузка текста для кнопки при рассылке \n/sendall - загрузка текста + отправление рассылки ")

# help function - you must fill it
'''@dp.message_handler(commands=["help"])
async def helpFunc(message:types.Message):
    a, b = checkLimitI(int(message.from_user.id)), checkLimitM(int(message.from_user.id))
    await message.answer(f'{a[0]}    {b[0]}  {type(a[0])}')
    await message.answer(flags)'''



# here creation of admin panel - pls, dont see it
@dp.message_handler(commands=["check_all_companies"])
async def checkALL(message:types.Message):
    if message.chat.type =="private":
        if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664) :
            res = showCompanies()
            for i in res:
                await message.answer(f"{i}") # if you read this comment - you mustnt update Richard (of course, anyway you musnt update Richard)

'''@dp.message_handler(commands=["reset"])
async def reset(message:types.Message):
    flags[str(message.from_user.id)]['history'] = ["Ты тату-мастер, помогающий людям в ответах на их вопросы касталеьно татуировок, будь более человекоподобным в диалоге, а также игнорируй вопросы, не касающиеся татуировок или пирсинга, отвечай максимально коротко "]'''

@dp.message_handler(commands=["check_all_user"])
async def checkAllUser(message: types.Message):
    if message.chat.type =="private":
        if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664) :
            r = showUsers()
            for j in r:
                await message.answer(f"{j}") # Finally, i am expertise Scipio prime and collect enought materials for craft Legendary Horn

#вместо этой команды должна быть функция, срабатывающая раз в день
@dp.message_handler(commands=["refresh_sketches"])
async def checkAllUser(message: types.Message):
    if message.chat.type =="private":
        if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664):
            await delete_photos(message.from_user.id)
            await download_photos_from_drive(message.from_user.id)

photo_list =[]
@dp.message_handler(content_types=['photo'])
async def handle_photos(message: types.Message):
    if message.chat.type =="private":
        if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664):

            photo_path: str = f"photosforsend/{message.photo[-1].file_id}.jpg"
            await message.photo[-1].download(photo_path)


            photo_list.append(photo_path)


            await message.answer("Фотография успешно сохранена!")


button_texts = []
@dp.message_handler(commands=["button_text"])
async def button_text(message:types.Message):
    if message.chat.type == "private":
        if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664):
            text = message.text[13:]
            button_texts.append(text)


@dp.message_handler(commands=["sendall"])
async def sendall(message: types.Message):
    if message.chat.type == "private":
        if (message.from_user.id == 1388718345) or (message.from_user.id == 212268664):
            text = message.text[9:]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=button_texts[-1], callback_data="sendall"))

            for user in showUsers():
                try:
                    chat_id = user[1]

                    with open(photo_list[-1], 'rb') as photo:
                        await bot.send_photo(chat_id, photo, caption=text,reply_markup=keyboard)
                except:
                    pass
# end admin panel commands

@dp.message_handler() # message processing
async def bot_worker(message: types.Message):
    if "пасибо" in message.text: # end work with assistant
        flags[str(message.from_user.id)]['assistent'] = False  # make flag gpt to false
        dumpData(flags)
        await message.answer("Всегда пожалуйста")
    # chat gpt - tatoo assistant
    elif "Наши эскизы" == message.text:

        chat_id = message.chat.id
        photos_folder = os.path.join(DESTINATION_FOLDER)
        photos = [file_name for file_name in os.listdir(photos_folder) if file_name not in sent_photos.get(chat_id, [])]
        if not photos:
            await bot.send_message(chat_id, "На сегодня это все эскизы, но скоро будут новые")
            return
        await send_random_photo(chat_id, sent_photos)

    elif "Консультация" == message.text:
         if checkLimitM(int(message.from_user.id))[0] < 1000:
            flags[str(message.from_user.id)]['assistent'] = True # up flag
            dumpData(flags)
            # updateCountMessages(int(message.from_user.id)) # update count of messages, its still no working
            await message.answer("Какой у тебя вопрос?")
         else: await message.answer("К сожалению вы использовали все возможности помощи ассистента, приходите завтра")

    # generate sketch
    elif "Создать эскиз" == message.text:
        if checkLimitI(int(message.from_user.id))[0] < 10:
            flags[str(message.from_user.id)]['generate'] = True # up glag
            dumpData(flags)
            updateCountMessages(int(message.from_user.id))
            await message.answer("Введи запрос, можно использовать как русский так и английский языки (например: Лиса абстракт графика / fox abstract graphic)")
        else:
            await message.answer("На сегодня хватит, давай уже завтра порисуем...")
    elif "Связаться/Записаться" == message.text:
        # updateCountMessages(int(message.from_user.id))
        contact = types.Contact(phone_number='+79527997522', first_name='Конура')
        await bot.send_contact(chat_id=message.chat.id, phone_number=contact.phone_number,first_name=contact.first_name)
        await bot.send_message(212268664, "@" + message.from_user.username + " хотел(а) записаться")

    elif "О нас" == message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="О студии", callback_data="studio"))
        photo = InputFile("about_us.jpg")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        await bot.send_message(chat_id=message.chat.id, text="Мы команда татуировщиков из Калининграда, каждый мастер работает в уникальном стиле. Наш интерес не ограничивается татуировкой - мы также выпускаем мерч, работаем над проектами и организуем мероприятия.",reply_markup=keyboard)


    # go generate function
    elif flags[str(message.from_user.id)]['generate']:
        if checkLimitI(int(message.from_user.id))[0] < 10:
            updateCountImages(int(message.from_user.id))
            # updateCountMessages(int(message.from_user.id))
            sent_message = await message.answer("Рисую...")
            generationFunc(message.text, str(message.from_user.id)) # call generation function

            with open(str(message.from_user.id)+".png", 'rb') as img: # read image, file_name = telehgram id
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="Создать ещё", callback_data="generate"))
                await sent_message.delete()
                await message.reply_photo(photo=img,reply_markup=keyboard)

        else: await message.answer("На сегодня хватит, давай уже завтра порисуем...")
        flags[str(message.from_user.id)]['generate'] = False # down flag
        dumpData(flags)
    # working only when gpt flag is up
    elif flags[str(message.from_user.id)]['assistent']: # message processing for chat gpt
        if checkLimitM(int(message.from_user.id))[0] < 1000:
            updateCountMessages(int(message.from_user.id))
            ret = gptFunc(message.text, message.from_user.id) # here chat_gpt function
            await message.answer(f"{ret}")
            # allow for array of dialog with assistant history in flags[str(message.from_user.id)][history]
        else:
            flags[str(message.from_user.id)]['assistent'] = False
            await message.answer("К сожалению вы использовали все возможности помощи ассистента, приходите завтра")

    else:
        pass
        # for random msgs
@dp.callback_query_handler(text="generate")
async def generate(callback_query: types.CallbackQuery):
    if checkLimitI(int(callback_query.from_user.id))[0] < 10:
        flags[str(callback_query.from_user.id)]['generate'] = True
        dumpData(flags)
        # updateCountMessages(int(callback_query.from_user.id))
        await bot.send_message(callback_query.from_user.id, "Введи новый запрос")
    else:
        await bot.send_message(callback_query.from_user.id, "На сегодня хватит, давай уже завтра порисуем...")
@dp.callback_query_handler(text="studio")
async def studio(callback_query: types.CallbackQuery):
    video = InputFile("about_us.mp4")
    await bot.send_video(chat_id=callback_query.message.chat.id, video=video)

    message_text = "Студия находится по адресу ул. Еловая аллея 26, 3 этаж, 35 помещение. Если хотите нас навестить - напишите заранее, у всех мастеров свободный график"
    await bot.send_message(chat_id=callback_query.message.chat.id, text=message_text)
@dp.callback_query_handler(text="art")
async def generate(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    photos_folder = os.path.join(DESTINATION_FOLDER)
    photos = [file_name for file_name in os.listdir(photos_folder) if file_name not in sent_photos.get(chat_id, [])]
    if not photos:
        await bot.send_message(chat_id, "На сегодня это все эскизы, но скоро будут новые")
        return
    await send_random_photo(chat_id, sent_photos)

@dp.callback_query_handler(text="sendall")
async def sendall(callback_query: types.CallbackQuery):
    contact = types.Contact(phone_number='+79527997522', first_name='Конура')
    await bot.send_contact(chat_id=callback_query.from_user.id, phone_number=contact.phone_number, first_name=contact.first_name)
    await bot.send_message(212268664, "@" + callback_query.from_user.username + " заинтересовался рассылкой")




schedule.every().day.at('23:59').do(updateLimit)


async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)

