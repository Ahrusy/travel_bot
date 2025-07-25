import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌦️ Погода"), KeyboardButton(text="💱 Курсы валют")],
        [KeyboardButton(text="🧭 Переводчик"), KeyboardButton(text="🌍 О стране")],
    ],
    resize_keyboard=True
)

class Form(StatesGroup):
    waiting_for_city = State()
    waiting_for_translate = State()
    waiting_for_country = State()

bot = Bot(token="ВАШ_ТОКЕН")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Выбери функцию:", reply_markup=main_kb)

@dp.message()
async def main_handler(message: types.Message, state: FSMContext):
    text = message.text
    if text == "🌦️ Погода":
        await message.answer("Введи город:")
        await state.set_state(Form.waiting_for_city)
    elif text == "💱 Курсы валют":
        await message.answer("Курс валют: 1 USD = 75 RUB (пример)")
    elif text == "🧭 Переводчик":
        await message.answer("Введи текст для перевода:")
        await state.set_state(Form.waiting_for_translate)
    elif text == "🌍 О стране":
        await message.answer("Введи название страны:")
        await state.set_state(Form.waiting_for_country)
    else:
        await message.answer("Не понял. Используй кнопки.", reply_markup=main_kb)

@dp.message(StateFilter(Form.waiting_for_city))
async def city_handler(message: types.Message, state: FSMContext):
    city = message.text
    # Здесь должна быть логика вызова API погоды, пока заглушка:
    await message.answer(f"Погода в {city} - солнечно, +25°C")
    await state.clear()

@dp.message(StateFilter(Form.waiting_for_translate))
async def translate_handler(message: types.Message, state: FSMContext):
    text = message.text
    # Заглушка перевода:
    await message.answer(f"Перевод: {text} (английский)")
    await state.clear()

@dp.message(StateFilter(Form.waiting_for_country))
async def country_handler(message: types.Message, state: FSMContext):
    country = message.text
    # Заглушка инфо о стране:
    await message.answer(f"Информация о стране {country}")
    await state.clear()

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
