import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from asgiref.sync import sync_to_async
from webapp.models import TelegramUser
from .utils import is_valid_jwt_format, InvalidJWT


async def create_user_if_not_exist(telegram_id: int, telegram_username: str, jwt_token: str):
    user = TelegramUser.objects.filter(telegram_id=telegram_id).exists()
    if not user:
        if not is_valid_jwt_format(jwt_token):
            raise InvalidJWT()

        user = TelegramUser.objects.create(telegram_id=telegram_id,
                                           telegram_username=telegram_username,
                                           jwt_token=jwt_token)
    return user


