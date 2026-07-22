import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from api.scheduler import start_scheduler

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    asyncio.create_task(start_scheduler(bot)) # start scheduler in beckground
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')