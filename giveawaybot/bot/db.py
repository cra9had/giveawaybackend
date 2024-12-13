from datetime import datetime
import os, django
from typing import Sequence, Optional

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
from asgiref.sync import sync_to_async
from webapp.models import TelegramUser, TelegramChannel, GiveAway
from .utils import is_valid_jwt_format, InvalidJWT


async def create_user_if_not_exist(telegram_id: int, telegram_username: str, first_name: str, jwt_token: str):
    user = TelegramUser.objects.filter(telegram_id=telegram_id).exists()
    if not user:
        if not is_valid_jwt_format(jwt_token):
            raise InvalidJWT()

        user = TelegramUser.objects.create(telegram_id=telegram_id,
                                           telegram_username=telegram_username,
                                           first_name=first_name,
                                           jwt_token=jwt_token)
    return user


async def get_user_channels(telegram_id: int) -> Sequence[TelegramChannel]:
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    return TelegramChannel.objects.filter(owner=user)


async def create_channel(chat_id: int, owner_telegram_id: int, channel_name: str) -> TelegramChannel:
    owner = TelegramUser.objects.get(telegram_id=owner_telegram_id)
    channel = TelegramChannel.objects.create(owner=owner,
                                             chat_id=chat_id,
                                             channel_name=channel_name)
    return channel


async def create_giveaway(
    channel_pk: int, title: str, description: str, end_datetime: datetime, winners_count: int,
    is_referral_system: bool, referral_invites_count: int = 0, terms_of_participation: dict = {},
    image: Optional[str] = None, show_image_above_text: bool = False,
):
    channel = TelegramChannel.objects.get(pk=channel_pk)
    today = datetime.now().strftime('%Y-%m-%d')

    if terms_of_participation:
        terms_of_participation["deposit"]["starting_period"] = today
        terms_of_participation["bet"]["starting_period"] = today
    return GiveAway.objects.create(
        channel=channel,
        title=title,
        description=description,
        end_datetime=end_datetime,
        winners_count=winners_count,
        is_referral_system=is_referral_system,
        referral_invites_count=referral_invites_count,
        terms_of_participation=terms_of_participation,
        image=image,
        show_media_above_text=show_image_above_text,
    )

