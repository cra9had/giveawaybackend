import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
dp = Dispatcher()


router = Router(name=__name__)


@router.message(Command("help", "start"))
async def command_start_handler(message: Message):

    APP_BASE_URL = os.getenv('APP_BASE_URL')

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Открыть Розыгрыш', web_app=WebAppInfo(url=f'{APP_BASE_URL}'))
    )

    await message.answer("Вас приветствует GiveAway Bot", reply_markup=builder.as_markup())


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
