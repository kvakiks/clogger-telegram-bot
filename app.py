import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import logging
from aiogram import Bot, Dispatcher
from handlers.user import user      # Добавить админ-панель

from database.engine import create_db


TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)


# Запуск процесса поллинга новых апдейтов
async def main():
    await create_db()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())