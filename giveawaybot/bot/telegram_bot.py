import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from aiogram.utils.payload import decode_payload
from dotenv import load_dotenv

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from django.core.management import call_command

from .db import create_user_if_not_exist
from .utils import InvalidJWT

load_dotenv()

router = Router(name=__name__)


@router.message(CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject):
    args = command.args
    jwt_token_arg = args
    try:
        user = await create_user_if_not_exist(message.chat.id, message.chat.username, jwt_token_arg)
    except InvalidJWT:
        return await message.answer("Invalid JWT")
    await message.answer("Вас приветствует GiveAway Bot")


async def run_command_in_thread():
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, call_command)
