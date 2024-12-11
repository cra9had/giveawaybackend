import asyncio
import os

from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as redis
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from django.core.management.base import BaseCommand
from django.conf import settings
from bot.routers import start, create_giveaway


load_dotenv()


class Command(BaseCommand):
    help = "Start telegram bot"

    def handle(self, *args, **options):
        print("Starting telegram bot")
        redis_client = redis.Redis.from_url("redis://localhost:6379/3")
        redis_storage = RedisStorage(redis=redis_client)

        dp = Dispatcher(storage=redis_storage)
        dp_bot = Bot(settings.TELEGRAM_API_TOKEN,
                     default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        dp.include_routers(start.router, create_giveaway.router)

        async def startup(dispatcher: Dispatcher, bot: Bot):
            print("Telegram bot started!")

        dp.startup.register(startup)

        loop.run_until_complete(dp.start_polling(dp_bot, skip_updates=True))
