import httpx
from config import *

async def get_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
        if r.status_code != 200:
            return f"❌ Не удалось найти город '{city}'. Попробуйте ещё раз."
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
        r = await client.post(TRANSLATE_API, data={
            "q": text, "source": "auto", "target": to_lang, "format": "text"
        })
        if r.status_code != 200:
            return "❌ Ошибка перевода."
        return r.json()["translatedText"]

async def get_country_info(country: str):
    url = f"https://restcountries.com/v3.1/name/{country}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            return f"❌ Не удалось найти страну '{country}'."
        d = r.json()[0]
        languages = ", ".join(d['languages'].values()) if d.get('languages') else "N/A"
        currencies = ", ".join([v['name'] for v in d.get('currencies', {}).values()]) if d.get('currencies') else "N/A"
        capital = d['capital'][0] if d.get('capital') else "N/A"
        return (
            f"🌍 Страна: {d['name']['common']}\n"
            f"🏙️ Столица: {capital}\n"
            f"🗣️ Языки: {languages}\n"
            f"💰 Валюты: {currencies}"
        )
