import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from django.core.management.base import BaseCommand

from ...telegram_bot import router


load_dotenv()


class Command(BaseCommand):
    help = "Start telegram bot"

    def handle(self, *args, **options):
        print("Starting telegram bot")

        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        dp = Dispatcher()
        dp_bot = Bot(TOKEN)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        dp.include_router(router)

        async def startup(dispatcher: Dispatcher, bot: Bot):
            print("Telegram bot started!")

        dp.startup.register(startup)

        loop.run_until_complete(dp.start_polling(dp_bot, skip_updates=True))
