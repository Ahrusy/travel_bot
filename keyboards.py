from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌦️ Погода"), KeyboardButton(text="🗺️ Достопримечательности")],
        [KeyboardButton(text="💱 Курсы валют"), KeyboardButton(text="🧭 Переводчик")],
        [KeyboardButton(text="📌 Мои заметки"), KeyboardButton(text="🌍 О стране")],
    ],
    resize_keyboard=True
)
