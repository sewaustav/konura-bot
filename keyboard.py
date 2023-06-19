from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

assistent = KeyboardButton("Консультация")
generate = KeyboardButton("Создать эскиз")
info_btn = KeyboardButton("О нас")
contact = KeyboardButton("Связаться/Записаться")
sketch = KeyboardButton("Наши эскизы")

telegramKeyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(assistent, generate).row(sketch,info_btn).row(contact)


