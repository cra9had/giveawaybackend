from django.core.exceptions import ValidationError
from rest_framework.authentication import BaseAuthentication

from .models import TelegramUser


class TelegramAuthBackend(BaseAuthentication):
    """Telegram Authentication"""

    def authenticate(self, request, telegram_id=None, chat_id=None, **kwargs) -> TelegramUser | None:
        try:
            telegram_user: TelegramUser = TelegramUser.objects.get(
                telegram_id=telegram_id
            )
            if telegram_user.check_chat_id(chat_id):
                return telegram_user
            raise ValidationError("Chat id is incorrect")

        except TelegramUser.DoesNotExist as error:
            raise ValidationError(
                f"Telegram user with {telegram_id} id not found"
            ) from error

    def get_user(self, user_id) -> TelegramUser | None:
        try:
            return TelegramUser.objects.get(pk=user_id)
        except TelegramUser.DoesNotExist:
            return None
