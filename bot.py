import logging

from aiogram import Bot, Dispatcher

from config import TOKEN, LOG_LEVEL
from handlers import router

logging.basicConfig(level=LOG_LEVEL)

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(router)
