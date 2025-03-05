from datetime import datetime
import asyncio
import random

from aiogram import Bot
from app.databases import birthday, birthday_reminder, db_select_id
import requests
from bs4 import BeautifulSoup
from config import API_KEY, MY_ID


async def open_birthday(bot: Bot):
    func_txt = await birthday()
    if func_txt != "none":
        for bot_id in await db_select_id():
            try:
                await bot.send_message(bot_id, f'{func_txt}')
            except Exception as e:
                await bot.send_message(MY_ID, f'Ошибка при отправке сообщения пользователю {bot_id}: {e}')


async def open_birthday_reminder(bot: Bot):
    func_txt = await birthday_reminder()
    if func_txt != "none":
        for bot_id in await db_select_id():
            try:
                await bot.send_message(bot_id, f'{func_txt}')
            except Exception as e:
                await bot.send_message(MY_ID, f'Ошибка при отправке сообщения пользователю {bot_id}: {e}')


async def currency():
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    bitcoin = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC').json()
    eth = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=ETH').json()

    usd = data['Valute']['USD']['Value']
    eur = data['Valute']['EUR']['Value']
    amd = data['Valute']['AMD']['Value']

    bitcoin = bitcoin['data']['rates']['USD']
    eth = eth['data']['rates']['USD']

    return (f'Доллар - {usd:.2f}руб.\nЕвро - {eur:.2f}руб.\n1000руб. - {100 / amd * 1000:.0f}драм\n\n'
            f'BITCOIN - {bitcoin}\nETH - {eth}')


async def get_weather_forecast(api_key=API_KEY, city="Krasnodar", days=5):
    # Запрос к API
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # для получения данных в °C
        "lang": "ru"  # перевод описания на русский
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверка на ошибки
        data = response.json()

        # Группировка данных по дням
        forecasts = {}
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if date not in forecasts:
                forecasts[date] = []
            forecasts[date].append(item)

        # Выборка данных на указанное количество дней
        selected_dates = sorted(forecasts.keys())[:days]
        result = []
        for date in selected_dates:
            day_data = forecasts[date]
            # Пример агрегации данных (можно выбрать среднее или пиковые значения)
            temp_min = min(f["main"]["temp_min"] for f in day_data)
            temp_max = max(f["main"]["temp_max"] for f in day_data)
            description = day_data[0]["weather"][0]["description"]  # берем первое описание

            result.append({
                "date": date,
                "temp_min": temp_min,
                "temp_max": temp_max,
                "description": description,
                "humidity": day_data[0]["main"]["humidity"]
            })
        if result:
            weekday_dict = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота',
                            6: 'Воскресенье'}
            date_txt = "Прогноз погоды в\nКраснодаре на 5 дней:\n---\n"
            for day in result:
                week_day = weekday_dict[datetime.strptime(day['date'], "%Y-%m-%d").weekday()]
                day_split = day['date'].split("-")
                date_txt += f"{week_day} - {day_split[2]}.{day_split[1]}.{day_split[0]}:\n"
                date_txt += f"от {day['temp_min']}°C до {day['temp_max']}°C\n"
                date_txt += f"{day['description'].capitalize()}\n"
                date_txt += f"---\n"

            return date_txt[:-4]

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None


async def anekdot_dey():
    url = "https://anekdotov.net/anekdot/day/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        anekdot_block = soup.find('div', class_='anekdot')
        if anekdot_block:
            anekdot_text = anekdot_block.get_text(strip=True)
            return anekdot_text


async def anekdot_random():
    url = "https://anekdotov.net/anekdot/day/"
    response = requests.get(url)
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        # Находим все блоки с анекдотами (элементы с классом anekdot)
        anekdots_blocks = soup.find_all('div', class_='anekdot')

        if anekdots_blocks:
            random_anekdot_block = random.choice(anekdots_blocks)
            random_anekdot_text = random_anekdot_block.get_text(strip=True)
            return f"{random_anekdot_text}"
        else:
            return "На странице не найдено анекдотов."


async def all_func(bot: Bot):
    for bot_id in await db_select_id():
        try:
            await bot.send_message(bot_id, f'Анекдот дня:\n{await anekdot_random()}\n\n'
                                           f'Курсы валют:\n{await currency()}\n\n'
                                           f'{await get_weather_forecast()}')
        except Exception as e:
            await bot.send_message(MY_ID, f'Ошибка при отправке анекдота пользователю {bot_id}: {e}')


if __name__ == '__main__':
    print(asyncio.run(get_weather_forecast()))
