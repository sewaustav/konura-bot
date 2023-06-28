from config import *
import math
import logging
from keyboard import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, InputFile
from aiogram.dispatcher.filters import Command, Text
from aiogram import Bot, Dispatcher, executor, types
import openai
import json
from base64 import b64decode
import schedule
import asyncio
import time
from random import randint, choice
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload



# -------- THIS CODE WAS CREATED BY MAKSONCHIK SEVCHIK AND VOVCHIK --------
# -------------------------- BEDOLAGA COMPANY -----------------------------
# ------------------------ TATTOO BOT-ASSISTANT ---------------------------


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

openai.api_key = OpenAITOKEN  # init open ai api token


# generation image function
def generationFunc(message, name):  # message - prompt, name - tg_id(only use for create name of file)
    image_response = openai.Image.create(
        prompt=message + ".нужен только эскиз тату, только просто рисунок без частей тела.",  # prompt + settings
        n=1,
        size='512x512',
        response_format='b64_json'
    )

    with open(name + '.json', "w") as file:  # get image data to json
        json.dump(image_response, file, indent=4, ensure_ascii=False)

    image_data = b64decode(image_response['data'][0]['b64_json'])  # get image data
    file_name = name + ".png"

    with open(file_name, 'wb') as file:  # put image to file
        file.write(image_data)


# chat gpt
def gptFunc(message, user):
    array = flags[str(user)]['history']  # get history
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




    except:
        pass
    # return data to user

    reply = response.choices[0].message.content
    array.append(reply)

    return reply




# Classes and functions for portfolio button
class GoogleDriveDownloader:
    def __init__(self, google_ip_key, google_drive_folder, local_destination_folder):
        self.google_ip_key = google_ip_key
        self.google_drive_folder = google_drive_folder
        self.local_destination_folder = local_destination_folder
        self.drive_service = build('drive', 'v3', developerKey=google_ip_key)

    async def download_photos(self, user_id):
        results = self.drive_service.files().list(
            q=f"'{self.google_drive_folder}' in parents and trashed=false").execute()
        items = results.get('files', [])

        if not items:
            print('Поражение, фотки не найдены')
            await bot.send_message(user_id, "При загрузке фотографий возникла ошибка")
            return

        for item in items:
            file_id = item['id']
            file_name = item['name']
            destination = os.path.join(self.local_destination_folder, file_name)
            request = self.drive_service.files().get_media(fileId=file_id)

            with io.FileIO(destination, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

            print(f'Победа, файл "{file_name}" успешно загружен.')

        await bot.send_message(user_id, "Все фотографии успешно загружены")


class PhotoDeleter:
    def __init__(self, destination_folder):
        self.destination_folder = destination_folder

    async def delete_photos(self, chat_id):
        photos_folder = os.path.join(self.destination_folder)

        if not os.path.exists(photos_folder):
            print('Папка photos не существует')
            return

        for file_name in os.listdir(photos_folder):
            file_path = os.path.join(photos_folder, file_name)
            os.remove(file_path)
            print(f'Файл "{file_name}" удален.')

        print('Все фотографии удалены.')
        await bot.send_message(chat_id, "Все фотографии успешно удалены")


class PhotoSender:
    MAX_MEDIA_COUNT = 10  # Максимальное количество фотографий в одной группе media

    async def send_photos_from_folder(self, folder_path, chat_id):
        photo_files = self.get_photo_files(folder_path)
        media_groups = self.split_photos_into_groups(photo_files, self.MAX_MEDIA_COUNT)

        for media_group in media_groups:
            media = []
            for photo_file in media_group:
                with open(photo_file, 'rb') as photo:
                    photo_bytes_io = io.BytesIO(photo.read())
                    media.append(types.InputMediaPhoto(media=photo_bytes_io))
            await bot.send_media_group(chat_id, media=media)

    def get_photo_files(self, folder_path):
        photo_files = []
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and self.is_photo_file(file_name):
                photo_files.append(file_path)
        return photo_files

    def is_photo_file(self, file_name):
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        _, extension = os.path.splitext(file_name)
        return extension.lower() in valid_extensions

    def split_photos_into_groups(self, photo_files, max_count):
        groups = []
        num_groups = math.ceil(len(photo_files) / max_count)
        for i in range(num_groups):
            start = i * max_count
            end = (i + 1) * max_count
            groups.append(photo_files[start:end])
        return groups


# create dict for flags
with open('data.json', 'r') as file:
    # load data to dict
    flags = json.load(file)


# this dictionary its only for shot time data, this is consist only flags and array of dialog
def dumpData(data):
    with open('data.json', 'w') as file:
        json.dump(data, file)


def loadData():
    with open("data.json", "r") as file:
        flags = json.load(file)





# start function
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    loadData()
    keyFlags = list(flags.keys())
    await bot.send_message(842949149,
                           "@" + str(message.from_user.username) + "  нажал на команду старт. Задудосить его?")
    await bot.send_message(1388718345,
                           "@" + str(message.from_user.username) + "  нажал на команду старт.")
    if str(message.from_user.id) in keyFlags:

        pass
        # flags[str(message.from_user.id)] = {'username': message.from_user.username, 'assistent': False, 'generate': False, 'message':0, 'images':0, 'history': ["Ты тату-мастер, помогающий людям в ответах на их вопросы касталеьно татуировок, будь более человекоподобным в диалоге, а также игнорируй вопросы, не касающиеся татуировок или пирсинга, отвечай максимально коротко"]} # here i make flags with dictionary and also make setting for chat gpt role
    else:
        us_name = message.from_user.username
        if type(us_name) == None:
            us_name = str(message.from_user.id) + "NOUSERNAME"
        flags[str(message.from_user.id)] = {'username': us_name, 'assistent': False, 'generate': False, 'message': 0,
                                            'images': 0,'history': [
                'Прими на себя данную роль: Я Конура бот, эксперт по татуировкам, пирсингу и удалению тату. Я готов помочь и консультировать тебя. Если у тебя есть какие-либо вопросы, не стесняйся задавать.Студия Конура находится по адресу ул. Еловая аллея 26, 3 этаж, помещение 35. Мы работаем ежедневно с 12:00 до 22:00. Номер телефона для связи +79527997522 (Никита)Записаться на консультацию или сеанс можно нажав на кнопку "Связаться / записаться" внизу этого чата.Важно отметить, что мы не делаем татуировки лицам, которым нет 18 лет, если нет согласия родителей. Однако мы делаем исключение, если есть разрешение родителей.В нашей студии мы не предоставляем услуги по пирсингуВ нашей студии мы не предоставляем услуги по удалению татуировок.Минимальная стоимость татуировки в студии Конура составляет 3000 рублей. Мы также предлагаем подарочные сертификаты стоимостью от 1000 рублей, которые можно потратить на татуировку или обменять на наш мерч. Чтобы приобрести сертификат, тебе нужно прийти к нам в студию или заказать доставку по Калининграду. Для этого просто нажми на кнопку "Связаться/Записаться".В студии Конура мы также продаем мерч с принтами от отечественных татуировщиков, обычно это футболки или худи. Наш мерч обновляется с разной периодичностью.Отзывы о работе студии Конура можно найти на платформах 2ГИС, Яндекс и Google. Также мы активны в социальных сетях, у нас есть группа Вконтакте и профиль в Instagram. Можешь посетить эти страницы, чтобы увидеть нашу работу и быть в курсе новостей.В нашей студии работает несколько мастеров с различными стилями:Никита Наумов специализируется на технике дотворк.Вера Богданова делает неотрадиционные татуировки.Эдгар Коженков владеет стилями дарк реализм, блекворк и перекрытия.Владимир Гусев делает цветные татуировки, предпочитая ньюскул стилистику и также выполняет перекрытия.Яна Котова занимается традиционной татуировкой.Таисия Иванова специализируется на олдскуле.Саша Сизионова создает линейно-пятновую графику.Любовь Ходова работает с графикой и реализмом.Также у нас часто бывают гостевые мастера с индивидуальными стилями. Они приезжают на короткий период времени. Обязательно сообщи мне, когда появится новый гостевой мастер. Если тебе интересны эскизы мастеров или их работы, просто нажми на кнопку "Портфолио мастеров" в этом чате. Если у тебя возникнут еще вопросы или понадобится помощь, я всегда готов помочь.']}  # here i make flags with dictionary and also make setting for chat gpt role
    dumpData(flags)
    await message.answer(
        f'Привет, {message.from_user.first_name}! Я чат-бот студии Конура, готов помочь с вопросами о татуировках и с удовольствием поделюсь информацией о наших мастерах или студии. Чтобы начать общение, нажми кнопку "Консультация". Если захочешь посмотреть портфолио мастеров, нажми на соответствующую кнопку. Для записи на сеанс или связи с мастерами используй кнопку "Связаться/записаться".',
        reply_markup=telegramKeyboard)
    if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
            message.from_user.id == 212268664):
        await message.answer(
            "/check_all_user - список всех пользователей бота \n/refresh_sketches - обновление фотографий с гугл диска \n/photo - загрузка фото для рассылки \n/button_text - загрузка текста для кнопки при рассылке \n/sendall - загрузка текста + отправление рассылки \n/count_images - счетчик всех фотографий сгенерированных ботом \n /video - загрузка видео для рассылки")



# send message to user
@dp.message_handler(commands=['sm'])
async def sm(message:types.Message):
    if message.from_user.id == 842949149 or message.from_user.id == 1388718345 or message.from_user.id == 212268664:
        c = 0
        idUser = ""
        messageU = ""
        for el in message.text:
            if c == 1:
                idUser += el
            elif c == 2:
                messageU += el
            if el == " " and c == 0:
                c+=1
            elif el == " " and c == 1:
                c+=1
        await bot.send_message(message.from_user.id, "сообщение отправленно")
        await bot.send_message(idUser, messageU)

# check count of all user
@dp.message_handler(commands=["check_all_user"])
async def helpFunc(message: types.Message):
    loadData()
    if message.chat.type == 'private':
        if message.from_user.id == 842949149 or message.from_user.id == 1388718345 or message.from_user.id == 212268664:
            try:
                await message.answer(len(list(flags.keys())))

            except Exception as err:
                await message.answer(err)
        if message.from_user.id == 842949149 or message.from_user.id == 1388718345:
            await message.answer(list(flags.keys()))

#count all images generations
@dp.message_handler(commands=['count_images'])
async def countImg(message: types.Message):
    loadData()
    if message.chat.type == 'private':
        if message.from_user.id == 842949149 or message.from_user.id == 1388718345 or message.from_user.id == 212268664:
            count = 0
            for el in list(flags.keys()):
                count += int(flags[el]['images'])
            await message.answer(count)

# deanon function
@dp.message_handler(commands=["send_info"])
async def seeAll(message: types.Message):
    loadData()
    if message.from_user.id == 842949149 or message.from_user.id == 1388718345:
        f = message.text
        f = f.replace('/send_info ', '', 1)
        a = flags[str(f)]['history']
        a = a[1:]
        if len(a) > 50:
            t = len(a) - 50
        else:
            t = 0
        for i in range(t, len(a)):
            await message.answer(a[i])

# check name by id
@dp.message_handler(commands=["check_name"])
async def seeAll(message: types.Message):
    loadData()
    if message.from_user.id == 1388718345 or message.from_user.id == 842949149:
        f = message.text
        f = f.replace('/check_name ', '', 1)
        user = await bot.get_chat(f)
        username = user.username if user.username else None
        await bot.send_message(message.from_user.id, text= "@" + username)

# just joke - dudos user function
@dp.message_handler(commands=['dudos'])
async def dudos(message: types.Message):
    if message.from_user.id == 842949149 or message.from_user.id == 1388718345:
        id_user = message.text
        id_user = id_user.replace('/dudos ', '', 1)
        id_user = int(id_user)
        for i in range(50):
            if id_user == 1388718345:

                await bot.send_message(id_user, "Сори за дудос")
            else:
                await bot.send_message(id_user, "[INFO] Error 403 Forbidden. Retry enter to system")
        if id_user == 1388718345:
            await bot.send_message(id_user, "задудошен севчиком")
        await bot.send_message(842949149, "Успешно")

# get limites
@dp.message_handler(commands=['limites'])
async def cccccc(message: types.Message):
    loadData()
    if message.from_user.id == 842949149 or message.from_user.id == 1388718345:
        for el in list(flags.keys()):
            try:
                await message.answer(
                    " @" + flags[el]["username"] + " ;" + str(flags[el]["images"]) + " ;" + str(flags[el]["message"]))
            except: pass


@dp.message_handler(commands=["refresh_sketches"])
async def checkAllUser(message: types.Message):
    loadData()
    if message.chat.type == "private":
        if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
                message.from_user.id == 212268664):
            deleter_tatoos = PhotoDeleter("Naumov/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Naumov/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Naumov_sketches = GoogleDriveDownloader(google_ip_key, "14A1zRdrdVsg-mIDF7p5_OA2GEAlaNrc-", "Naumov/эскизы")
            Naumov_tatoos = GoogleDriveDownloader(google_ip_key, "1Jb8KWkxZtGRMVggMvt2Zrl1OA1HkvsjP", "Naumov/работы")
            await Naumov_sketches.download_photos(message.from_user.id)
            await Naumov_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Эд Коженков/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Эд Коженков/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Ed_sketches = GoogleDriveDownloader(google_ip_key, "109fLFNJqH65LwaMAUH1FOvSUygrKLX2q",
                                                "Эд Коженков/эскизы")
            Ed_tatoos = GoogleDriveDownloader(google_ip_key, "1HnpEsSeWun5FoKXnIwZDlwIxmuTNY7C2", "Эд Коженков/работы")
            await Ed_sketches.download_photos(message.from_user.id)
            await Ed_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Любовь Ходова/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Любовь Ходова/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Lubov_sketches = GoogleDriveDownloader(google_ip_key, "1VFfj6a5qNM3NW0p4lcldke4XVnLJRrKk",
                                                   "Любовь Ходова/эскизы")
            Lubov_tatoos = GoogleDriveDownloader(google_ip_key, "1lO8XX8867mLx6GmCr92ZFQFHlboPFmp3",
                                                 "Любовь Ходова/работы")
            await Lubov_sketches.download_photos(message.from_user.id)
            await Lubov_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Яна Котова/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Яна Котова/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Kotova_sketches = GoogleDriveDownloader(google_ip_key, "1Uis31B-10S8vZimigldPgsm-LhQU-i6W",
                                                    "Яна Котова/эскизы")
            Kotova_tatoos = GoogleDriveDownloader(google_ip_key, "1WWByhPoHVnERDS_eUfd8pjrBYN3VpANZ",
                                                  "Яна Котова/работы")
            await Kotova_sketches.download_photos(message.from_user.id)
            await Kotova_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Таисия Иванова/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Таисия Иванова/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Kotova_sketches = GoogleDriveDownloader(google_ip_key, "1FAoMDJILl_b5ItRL3c1TvImgBIbbc88_",
                                                    "Таисия Иванова/эскизы")
            Kotova_tatoos = GoogleDriveDownloader(google_ip_key, "1bo19m_LrYtiXYzKVUdmidhbikGFLQ1-6",
                                                  "Таисия Иванова/работы")
            await Kotova_sketches.download_photos(message.from_user.id)
            await Kotova_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Саша Сизионова/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Саша Сизионова/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Sasha_sketches = GoogleDriveDownloader(google_ip_key, "1yxUpwhSS4OgSiPQWUSAGl6xwasYtISYs",
                                                   "Саша Сизионова/эскизы")
            Sasha_tatoos = GoogleDriveDownloader(google_ip_key, "1RyrIrGl_nWhBT2PO9O1-WCrDKF7yfZV8",
                                                 "Саша Сизионова/работы")
            await Sasha_sketches.download_photos(message.from_user.id)
            await Sasha_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Владимир Гусев/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Владимир Гусев/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Gusev_sketches = GoogleDriveDownloader(google_ip_key, "1zuRvYLPwOIfE-kdi_0DL1FcGeWSw4Ukl",
                                                   "Владимир Гусев/эскизы")
            Gusev_tatoos = GoogleDriveDownloader(google_ip_key, "1mU7ezWaEL-Maf3eH1BypjwCJhiL7VJBw",
                                                 "Владимир Гусев/работы")
            await Gusev_sketches.download_photos(message.from_user.id)
            await Gusev_tatoos.download_photos(message.from_user.id)

            deleter_tatoos = PhotoDeleter("Вера Богданова/работы")
            await deleter_tatoos.delete_photos(message.from_user.id)
            deleter_sketches = PhotoDeleter("Вера Богданова/эскизы")
            await deleter_sketches.delete_photos(message.from_user.id)
            Vera_sketches = GoogleDriveDownloader(google_ip_key, "1uoqPU1Ncs2L_HGTnL1VFA3BAfG4kAChA",
                                                  "Вера Богданова/эскизы")
            Vera_tatoos = GoogleDriveDownloader(google_ip_key, "1SMaAwkOucfciO8LeD-ty1usoIMesUB3J",
                                                "Вера Богданова/работы")
            await Vera_sketches.download_photos(message.from_user.id)
            await Vera_tatoos.download_photos(message.from_user.id)


photo_list = []
video_list = []
button_texts = []
message_list = []
text_message = ''

@dp.message_handler(content_types=['photo'])
async def handle_photos(message: types.Message):
    loadData()
    if message.chat.type == "private":
        if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
                message.from_user.id == 212268664):
            photo_path: str = f"photosforsend/{message.photo[-1].file_id}.jpg"
            await message.photo[-1].download(photo_path)

            photo_list.append(photo_path)

            await message.answer("Фотография успешно сохранена!")


@dp.message_handler(content_types=['video'])
async def handle_photos(message: types.Message):
    loadData()
    if message.chat.type == "private":
        if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
                message.from_user.id == 212268664):


            video_list.append(message.video)

            await message.answer("Видео успешно сохранено")


@dp.message_handler(commands=["sendall"])
async def sendall(message: types.Message):
    loadData()
    if message.chat.type == "private":
        if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
                message.from_user.id == 212268664):
            text = message.text[9:]
            if button_texts and photo_list and (not video_list):
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text=button_texts[-1], callback_data="sendall"))

                for user in list(flags.keys()):
                    try:
                        chat_id = int(user)

                        with open(photo_list[-1], 'rb') as photo:
                            await bot.send_photo(chat_id, photo, caption=text, reply_markup=keyboard)
                    except:
                        pass
            elif (not button_texts)  and photo_list and (not video_list):


                for user in list(flags.keys()):
                    try:
                        chat_id = int(user)
                        with open(photo_list[-1], 'rb') as photo:
                            await bot.send_photo(chat_id, photo, caption=text)


                    except:
                        pass

            elif (not button_texts)  and (not photo_list) and (not video_list):

                for user in list(flags.keys()):
                    try:
                        chat_id = int(user)

                        await bot.send_message(chat_id, text=text)
                    except:
                        pass
            elif button_texts and (not photo_list) and (video_list):
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text=button_texts[-1], callback_data="sendall",))
                for user in list(flags.keys()):
                    try:
                        chat_id = int(user)
                        last_video = video_list[-1]

                        # Получение file_id последнего видео
                        file_id = last_video.file_id

                        # Получение объекта файла видео по file_id
                        video_file = await bot.get_file(file_id)

                        # Получение пути к файлу видео на диске
                        video_path = video_file.file_path

                        # Сохранение видео на диск
                        await bot.download_file_by_id(file_id, video_path)
                        with open(video_path, 'rb') as video:
                            await bot.send_video(chat_id, video, caption=text,reply_markup=keyboard)

                    except:
                        pass
            elif (not button_texts)  and (not photo_list) and video_list:

                for user in list(flags.keys()):
                    try:
                        chat_id = int(user)
                        last_video = video_list[-1]

                        # Получение file_id последнего видео
                        file_id = last_video.file_id

                        # Получение объекта файла видео по file_id
                        video_file = await bot.get_file(file_id)

                        # Получение пути к файлу видео на диске
                        video_path = video_file.file_path

                        # Сохранение видео на диск
                        await bot.download_file_by_id(file_id, video_path)
                        with open(video_path, 'rb') as video:
                            await bot.send_video(chat_id, video, caption=text)
                    except:
                        pass
            photo_list.clear()
            video_list.clear()
            button_texts.clear()

@dp.message_handler(commands=["button_text"])
async def button_text(message: types.Message):
    loadData()
    if message.chat.type == "private":
        if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
                message.from_user.id == 212268664):
            text = message.text[13:]
            button_texts.append(text)
            await bot.send_message(message.from_user.id, text=text)

@dp.message_handler(commands=["send_video"])
async def button_text(message: types.Message):
    loadData()
    if message.chat.type == "private":
        if (message.from_user.id == 842949149) or (message.from_user.id == 1388718345) or (
                message.from_user.id == 212268664):
            last_video = video_list[-1]

            # Получение file_id последнего видео
            file_id = last_video.file_id

            # Получение объекта файла видео по file_id
            video_file = await bot.get_file(file_id)

            # Получение пути к файлу видео на диске
            video_path = video_file.file_path

            # Сохранение видео на диск
            await bot.download_file_by_id(file_id, video_path)
            with open(video_path, 'rb') as video:
                await bot.send_video(1388718345, video, caption="видео")
            video_list.clear()



@dp.message_handler()  # message processing
async def bot_worker(message: types.Message):
    loadData() # load data from json file
    if "Роналду" == message.text or "Роналдо" == message.text:
        await message.answer("SUIIIIIIIIIIIIII")
        await bot.send_message(842949149, "@" + str(message.from_user.id) + "  написал Роналду")
    if "Месси" == message.text:
        await message.answer("Messi, Messi")
        await message.answer("Ankara Messi, Ankara Messi")
        await message.answer("Ankara Messi, Ankara Messi")
        await message.answer("Ankara Messi, Ankara Messi")
        await message.answer("Ankara Messi, Ankara Messi")
        await message.answer("Ankara Messi, Ankara Messi")
        await message.answer("Ankara Messi, Ankara Messi")
        await message.answer("Ankara Messi... GOAL GOAL GOAL GOAL")
        await bot.send_message(842949149, "@" + str(message.from_user.id) + "  написал Месси")

    if "пасибо" in message.text:  # end work with assistant
        loadData()
        flags[str(message.from_user.id)]['assistent'] = False  # make flag gpt to false
        dumpData(flags)
        await message.answer("Всегда пожалуйста")

    # chat gpt - tatoo assistant
    elif "Портфолио мастеров" == message.text:

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text="Никита Наумов", callback_data="Naumov"))
        keyboard.add(types.InlineKeyboardButton(text="Эд Коженков", callback_data="Ed"))
        keyboard.add(types.InlineKeyboardButton(text="Любовь Ходова", callback_data="Hodova"))
        keyboard.add(types.InlineKeyboardButton(text="Яна Котова", callback_data="Kotova"))
        keyboard.add(types.InlineKeyboardButton(text="Таисия Иванова", callback_data="Ivanova"))
        keyboard.add(types.InlineKeyboardButton(text="Саша Сизионова", callback_data="Sasha"))
        keyboard.add(types.InlineKeyboardButton(text="Владимир Гусев", callback_data="Gusev"))
        keyboard.add(types.InlineKeyboardButton(text="Вера Богданова", callback_data="Vera"))
        photo = InputFile("we.jpg")
        await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=keyboard)


    # chat gpt assistant
    elif "Консультация" == message.text:
        loadData()
        flags[str(message.from_user.id)]['history'] = [
            'Прими на себя данную роль: Я Конура бот, эксперт по татуировкам, пирсингу и удалению тату. Я готов помочь и консультировать тебя. Если у тебя есть какие-либо вопросы, не стесняйся задавать.Студия Конура находится по адресу ул. Еловая аллея 26, 3 этаж, помещение 35. Мы работаем ежедневно с 12:00 до 22:00. Номер телефона для связи +79527997522 (Никита)Записаться на консультацию или сеанс можно нажав на кнопку "Связаться / записаться" внизу этого чата.Важно отметить, что мы не делаем татуировки лицам, которым нет 18 лет, если нет согласия родителей. Однако мы делаем исключение, если есть разрешение родителей.В нашей студии мы не предоставляем услуги по пирсингуВ нашей студии мы не предоставляем услуги по удалению татуировок.Минимальная стоимость татуировки в студии Конура составляет 3000 рублей. Мы также предлагаем подарочные сертификаты стоимостью от 1000 рублей, которые можно потратить на татуировку или обменять на наш мерч. Чтобы приобрести сертификат, тебе нужно прийти к нам в студию или заказать доставку по Калининграду. Для этого просто нажми на кнопку "Связаться/Записаться".В студии Конура мы также продаем мерч с принтами от отечественных татуировщиков, обычно это футболки или худи. Наш мерч обновляется с разной периодичностью.Отзывы о работе студии Конура можно найти на платформах 2ГИС, Яндекс и Google. Также мы активны в социальных сетях, у нас есть группа Вконтакте и профиль в Instagram. Можешь посетить эти страницы, чтобы увидеть нашу работу и быть в курсе новостей.В нашей студии работает несколько мастеров с различными стилями:Никита Наумов специализируется на технике дотворк.Вера Богданова делает неотрадиционные татуировки.Эдгар Коженков владеет стилями дарк реализм, блекворк и перекрытия.Владимир Гусев делает цветные татуировки, предпочитая ньюскул стилистику и также выполняет перекрытия.Яна Котова занимается традиционной татуировкой.Таисия Иванова специализируется на олдскуле.Саша Сизионова создает линейно-пятновую графику.Любовь Ходова работает с графикой и реализмом.Также у нас часто бывают гостевые мастера с индивидуальными стилями. Они приезжают на короткий период времени. Обязательно сообщи мне, когда появится новый гостевой мастер. Если тебе интересны эскизы мастеров или их работы, просто нажми на кнопку "Портфолио мастеров" в этом чате. Если у тебя возникнут еще вопросы или понадобится помощь, я всегда готов помочь.'
            ]
        flags[str(message.from_user.id)]['generate'] = False
        flags[str(message.from_user.id)]['assistent'] = True  # up flag
        dumpData(flags)
        await message.answer("Какой у тебя вопрос?")

    # Contact with us
    elif "Связаться/Записаться" == message.text:
        contact = types.Contact(phone_number='+79527997522', first_name='Конура')
        await bot.send_message(message.from_user.id, "Отправил твой запрос, ребята скоро свяжутся с тобой. Чтобы связаться сразу, напиши или позвони сюда")
        await bot.send_contact(chat_id=message.chat.id, phone_number=contact.phone_number,
                               first_name=contact.first_name)
        if message.from_user.id != 842949149:
            await bot.send_message(212268664, "@" + message.from_user.username + " хотел(а) записаться")

    # about us
    elif "О нас" == message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="О студии", callback_data="studio"))
        photo = InputFile("about_us.jpg")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        await bot.send_message(chat_id=message.chat.id,
                               text="Мы команда татуировщиков из Калининграда, каждый мастер работает в уникальном стиле. Наш интерес не ограничивается татуировкой - мы также выпускаем мерч, работаем над проектами и организуем мероприятия.",
                               reply_markup=keyboard)

    # image generation
    elif "Achtung, Achtung, die deutsche Soldaten, eine freundlichste Nachricht, die russischen Panzerkampfwagen marschieren nach Berlin." == message.text and message.from_user.id == 842949149:
        loadData()
        if flags[str(message.from_user.id)]['images'] < 10 or message.from_user.id == 842949149:

            flags[str(message.from_user.id)]['generate'] = True  # up glag
            dumpData(flags)

            await message.answer(
                "Введи запрос, можно использовать как русский так и английский языки (например: Лиса абстракт графика / fox abstract graphic)")
        else:
            await message.answer('На сегодня хватит, давай уже завтра порисуем...')


    # working only when gpt flag is up
    elif flags[str(message.from_user.id)]['assistent']:  # message processing for chat gpt
        loadData()
        if flags[str(message.from_user.id)]['message'] < 10000:
            flags[str(message.from_user.id)]['generate'] = False
            flags[str(message.from_user.id)]['message'] += 1
            ret = gptFunc(message.text, message.from_user.id)  # here chat_gpt function
            dumpData(flags)
            await message.answer(f"{ret}")
            # allow for array of dialog with assistant history in flags[str(message.from_user.id)][history]
        else:
            await message.answer('Вы исчерпали свой лимит сообщений...')

    # generate image
    elif flags[str(message.from_user.id)]['generate']:
        loadData()
        if flags[str(message.from_user.id)]['images'] < 10 and message.from_user.id == 842949149:
            sent_message = await message.answer("Рисую...")
            generationFunc(message.text, str(message.from_user.id))  # call generation function
            flags[str(message.from_user.id)]['images'] += 1
            with open(str(message.from_user.id) + ".png", 'rb') as img:  # read image, file_name = telehgram id
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="Создать ещё", callback_data="generate"))
                await sent_message.delete()
                await message.reply_photo(photo=img, reply_markup=keyboard)

            flags[str(message.from_user.id)]['generate'] = False  # down flag
            dumpData(flags)
        else:
            await message.answer('На сегодня хватит, давай уже завтра порисуем...')


    else:
        pass

# generation callback
@dp.callback_query_handler(text="generate")
async def generateNew(callback_query: types.CallbackQuery):
    loadData()
    if flags[str(callback_query.from_user.id)]['images'] < 10 and callback_query.from_user.id == 842949149:
        flags[str(callback_query.from_user.id)]['generate'] = True
        flags[str(callback_query.from_user.id)]['images'] += 1
        dumpData(flags)
        await bot.send_message(callback_query.from_user.id, "Введи новый запрос")
    else:
        await bot.send_message(callback_query.from_user.id, 'На сегодня хватит, давай уже завтра порисуем...')


@dp.callback_query_handler(text="studio")
async def studio(callback_query: types.CallbackQuery):
    loadData()
    video = InputFile("about_us.mp4")
    await bot.send_video(chat_id=callback_query.message.chat.id, video=video)

    message_text = "Студия находится по адресу ул. Еловая аллея 26, 3 этаж, 35 помещение. Если хотите нас навестить - напишите заранее, у всех мастеров свободный график"
    await bot.send_message(chat_id=callback_query.message.chat.id, text=message_text)


@dp.callback_query_handler(text="Naumov")
async def Naumov(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Naumov/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Naumov_cketches"))

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Никита делает небольшие и детальные татуировки в дотворк технике (точками). Если вам понравились его работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)


@dp.callback_query_handler(text="Naumov_cketches")
async def Naumov(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Naumov/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)

@dp.callback_query_handler(text="Ed")
async def Ed(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Эд Коженков/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Ed_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Эд работает в стилистиках дарк реализм и блекворк. Эти стили также отлично подходят для перекрытий старых тату. Если вам понравились его работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)


@dp.callback_query_handler(text="Ed_cketches")
async def Ed(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Эд Коженков/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Kotova")
async def Kotova(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Яна Котова/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Kotova_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Яна занимается традиционной татуировкой. Если вам понравились её работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Kotova_cketches")
async def Kotova(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Яна Котова/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Ivanova")
async def Ivanova(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Таисия Иванова/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Ivanova_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Таисия обычно говорит, что ее татуировки для панков, наверное это можно назвать олдскулом. Если вам понравились её работы, советую ознакомиться со свободными эскизами мастера.',
                           reply_markup=keyboard)


@dp.callback_query_handler(text="Ivanova_cketches")
async def Ivanova(callback_query: types.CallbackQuery):
    sender2 = PhotoSender()
    await sender2.send_photos_from_folder("Таисия Иванова/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Hodova")
async def Hodova(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Любовь Ходова/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Hodova_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Любовь делает татуирвоки в стиле графика и реализм. Если вам понравились её работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)


@dp.callback_query_handler(text="Hodova_cketches")
async def Hodova(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Любовь Ходова/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)


@dp.callback_query_handler(text="Sasha")
async def Sasha(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Саша Сизионова/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Sasha_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Линейно-пятновая графика - вот название стиля татуировок, в котором работает Саша.Если вам понравились её работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Sasha_cketches")
async def Sasha(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Саша Сизионова/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Gusev")
async def Gusev(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Владимир Гусев/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Gusev_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Вова делает татуировки в основном в блэк энд грей реализме и ньюскуле, хотя есть ощущение что он сможет исполнить татировку в любой стилистике. Если вам понравились его работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Gusev_cketches")
async def Gusev(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Владимир Гусев/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Vera")
async def Vera(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Вера Богданова/работы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Смотреть эскизы", callback_data="Vera_cketches"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Наверное Вера работает в стиле неотрад, хотя очевидно он у нее свой. Советую обратить внимание на ее работы со змеями - это определенно топ. Если вам понравились её работы, советую ознакомиться со свободными эскизами мастера',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Vera_cketches")
async def Gusev(callback_query: types.CallbackQuery):
    sender = PhotoSender()
    await sender.send_photos_from_folder("Вера Богданова/эскизы", callback_query.message.chat.id)
    keyboard = types.InlineKeyboardMarkup(one_time_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Вернуться к мастерам", callback_data="Masters"))
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Чтобы записаться на татуировку по эскизу мастера нажмите кнопку "связаться/записаться" в меню. Ребята свяжутся с вами и пригласят на сеанс',
                           reply_markup=keyboard)



@dp.callback_query_handler(text="Masters")
async def Masters(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Никита Наумов", callback_data="Naumov"))
    keyboard.add(types.InlineKeyboardButton(text="Эд Коженков", callback_data="Ed"))
    keyboard.add(types.InlineKeyboardButton(text="Любовь Ходова", callback_data="Hodova"))
    keyboard.add(types.InlineKeyboardButton(text="Яна Котова", callback_data="Kotova"))
    keyboard.add(types.InlineKeyboardButton(text="Таисия Иванова", callback_data="Ivanova"))
    keyboard.add(types.InlineKeyboardButton(text="Саша Сизионова", callback_data="Sasha"))
    keyboard.add(types.InlineKeyboardButton(text="Владимир Гусев", callback_data="Gusev"))
    keyboard.add(types.InlineKeyboardButton(text="Вера Богданова", callback_data="Vera"))
    photo = InputFile("we.jpg")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo, reply_markup=keyboard)



@dp.callback_query_handler(text="sendall")
async def sendall(callback_query: types.CallbackQuery):
    loadData()
    contact = types.Contact(phone_number='+79527997522', first_name='Конура')
    await bot.send_contact(chat_id=callback_query.from_user.id, phone_number=contact.phone_number,
                           first_name=contact.first_name)



    await bot.send_message(212268664, f"@{callback_query.from_user.username} заинтересовался рассылкой")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)