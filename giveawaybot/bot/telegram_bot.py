import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.management import call_command

load_dotenv()

router = Router(name=__name__)


@router.message(Command("help", "start"))
async def command_start_handler(message: Message):

    APP_BASE_URL = os.getenv('APP_BASE_URL')

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Открыть Розыгрыш', web_app=WebAppInfo(url=f'{APP_BASE_URL}'))
    )

    await message.answer("Вас приветствует GiveAway Bot", reply_markup=builder.as_markup())


async def run_command_in_thread():
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, call_command)
