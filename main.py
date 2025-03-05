import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import TOKEN
from app.handlers import router
from app.handlers_notes import router_notes
from app.handlers_admin import router_admin
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from app.func import open_birthday, open_birthday_reminder, all_func
from app.databases import delta_db


async def main():
    bot: Bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher()

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(delta_db, trigger='cron', hour=3, minute=7, start_date=datetime.now(), args=(dp,))
    scheduler.add_job(open_birthday, trigger='cron', hour=12, minute=00, start_date=datetime.now(), kwargs={"bot": bot})
    scheduler.add_job(open_birthday_reminder, trigger='cron', hour=12, minute=00, start_date=datetime.now(),
                      kwargs={"bot": bot})
    scheduler.add_job(all_func, trigger='cron', hour=15, minute=00, start_date=datetime.now(), kwargs={"bot": bot})
    scheduler.start()

    dp.include_routers(router, router_notes, router_admin)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print('Бот запущен!!!')
        logging.basicConfig(filename='DATA/logs.log', level=logging.INFO,
                            format='%(levelname)s (%(asctime)s): %(message)s (line: %(lineno)d) [%(filename)s]',
                            datefmt='%d.%m.%Y %H:%M:%S', filemode='w')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
