import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import httpx
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
TRANSLATE_API = os.getenv("TRANSLATE_API")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌦️ Погода"), KeyboardButton(text="🗺️ Достопримечательности")],
        [KeyboardButton(text="💱 Курсы валют"), KeyboardButton(text="🧭 Переводчик")],
        [KeyboardButton(text="📌 Мои заметки"), KeyboardButton(text="🌍 О стране")],
    ],
    resize_keyboard=True
)

notes_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить заметку")],
        [KeyboardButton(text="📋 Показать заметки")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True
)

class Form(StatesGroup):
    waiting_for_city = State()
    waiting_for_translate = State()
    waiting_for_country = State()
    waiting_for_note_action = State()
    waiting_for_new_note = State()
    waiting_for_sights = State()

user_notes = {}

sights_data = {
    "рим": [
        "Колизей",
        "Римский форум",
        "Пантеон",
        "Фонтан Треви",
        "Ватикан"
    ],
    "париж": [
        "Эйфелева башня",
        "Лувр",
        "Нотр-Дам",
        "Монмартр"
    ],
    "москва": [
        "Красная площадь",
        "Кремль",
        "Храм Василия Блаженного",
        "Третьяковская галерея"
    ],
    "италия": [
        "Колизей в Риме",
        "Пизанская башня",
        "Венецианские каналы",
        "Флорентийский собор"
    ]
}

async def get_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            return f"❌ Не удалось найти город '{city}'. Попробуйте ещё раз."
        data = r.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"🌡️ Погода в городе {city.title()}:\n{desc.capitalize()}, температура {temp}°C"

async def get_exchange_rate():
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            return "❌ Не удалось получить курсы валют."
        rates = r.json()["conversion_rates"]
        return (
            f"💱 Курсы валют по отношению к USD:\n"
            f"EUR: {rates.get('EUR', 'N/A')}\n"
            f"RUB: {rates.get('RUB', 'N/A')}\n"
            f"KZT: {rates.get('KZT', 'N/A')}"
        )

async def translate(text: str, to_lang='en'):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                TRANSLATE_API,
                json={
                    "q": text,
                    "source": "auto",
                    "target": to_lang,
                    "format": "text"
                },
                timeout=10
            )
            r.raise_for_status()
            data = r.json()
            return data.get("translatedText", "❌ Ошибка перевода.")
        except Exception as e:
            print("Ошибка перевода:", e)
            return "❌ Ошибка перевода."

async def get_country_info(country: str):
    async with httpx.AsyncClient() as client:
        url_full = f"https://restcountries.com/v3.1/name/{country}?fullText=true"
        r = await client.get(url_full)
        if r.status_code != 200:
            url_partial = f"https://restcountries.com/v3.1/name/{country}"
            r = await client.get(url_partial)
            if r.status_code != 200:
                return f"❌ Не удалось найти страну '{country}'."
        data = r.json()
        if not data:
            return f"❌ Не удалось найти страну '{country}'."
        d = data[0]
        languages = ", ".join(d.get('languages', {}).values()) if d.get('languages') else "N/A"
        currencies = ", ".join([v['name'] for v in d.get('currencies', {}).values()]) if d.get('currencies') else "N/A"
        capital = d['capital'][0] if d.get('capital') else "N/A"
        population = f"{d.get('population', 'N/A'):,}".replace(",", " ")
        region = d.get('region', 'N/A')

        return (
            f"🌍 Страна: {d['name']['common']}\n"
            f"🏙️ Столица: {capital}\n"
            f"👥 Население: {population}\n"
            f"🌐 Регион: {region}\n"
            f"🗣️ Языки: {languages}\n"
            f"💰 Валюты: {currencies}"
        )

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет, путешественник!\nЯ помогу тебе с полезной информацией в пути! 🚀",
        reply_markup=main_kb
    )

@dp.message(StateFilter(None))
async def main_handler(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    if text == "🌦️ погода":
        await message.answer("🌆 Введи название города:")
        await state.set_state(Form.waiting_for_city)
    elif text == "💱 курсы валют":
        result = await get_exchange_rate()
        await message.answer(result, reply_markup=main_kb)
    elif text == "🧭 переводчик":
        await message.answer("📝 Введи фразу для перевода на английский:")
        await state.set_state(Form.waiting_for_translate)
    elif text == "🌍 о стране":
        await message.answer("🌐 Введи название страны:")
        await state.set_state(Form.waiting_for_country)
    elif text == "📌 мои заметки":
        await message.answer("Выбери действие с заметками:", reply_markup=notes_kb)
        await state.set_state(Form.waiting_for_note_action)
    elif text == "🗺️ достопримечательности":
        await message.answer(
            "🗺️ Введи название города, чтобы узнать достопримечательности:\n(или нажми ⬅️ Назад)",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="⬅️ Назад")]],
                resize_keyboard=True
            )
        )
        await state.set_state(Form.waiting_for_sights)
    else:
        await message.answer("🤖 Не понял. Используй кнопки ниже.", reply_markup=main_kb)

@dp.message(StateFilter(Form.waiting_for_city))
async def process_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    weather = await get_weather(city)
    await message.answer(weather, reply_markup=main_kb)
    await state.clear()

@dp.message(StateFilter(Form.waiting_for_translate))
async def process_translate(message: types.Message, state: FSMContext):
    text_to_translate = message.text.strip()
    translated = await translate(text_to_translate)
    await message.answer(f"Перевод: {translated}", reply_markup=main_kb)
    await state.clear()

@dp.message(StateFilter(Form.waiting_for_country))
async def process_country(message: types.Message, state: FSMContext):
    country = message.text.strip()
    info = await get_country_info(country)
    await message.answer(info, reply_markup=main_kb)
    await state.clear()

@dp.message(StateFilter(Form.waiting_for_note_action))
async def notes_action_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    if text == "➕ добавить заметку":
        await message.answer("📝 Введи текст заметки:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.waiting_for_new_note)
    elif text == "📋 показать заметки":
        notes = user_notes.get(user_id, [])
        if notes:
            await message.answer("📚 Твои заметки:\n\n" + "\n\n".join(f"• {n}" for n in notes), reply_markup=notes_kb)
        else:
            await message.answer("⚠️ Заметок пока нет.", reply_markup=notes_kb)
    elif text == "⬅️ назад":
        await message.answer("Главное меню:", reply_markup=main_kb)
        await state.clear()
    else:
        await message.answer("Выбери действие из меню.", reply_markup=notes_kb)

@dp.message(StateFilter(Form.waiting_for_new_note))
async def add_new_note_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    note_text = message.text.strip()

    if not note_text:
        await message.answer("⚠️ Текст заметки не может быть пустым. Введи снова:")
        return

    notes = user_notes.setdefault(user_id, [])
    notes.append(note_text)

    await message.answer("✅ Заметка добавлена.", reply_markup=notes_kb)
    await state.set_state(Form.waiting_for_note_action)

@dp.message(StateFilter(Form.waiting_for_sights))
async def process_sights(message: types.Message, state: FSMContext):
    user_input = message.text.strip().lower()

    if user_input == "⬅️ назад":
        await message.answer("Главное меню:", reply_markup=main_kb)
        await state.clear()
        return

    city = user_input.split()[0]
    sights = sights_data.get(city)
    if sights:
        response = f"🗺️ Достопримечательности города {city.title()}:\n" + "\n".join(f"• {item}" for item in sights)
    else:
        response = f"❌ Извините, информации о достопримечательностях для '{city.title()}' пока нет."

    await message.answer(response)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
