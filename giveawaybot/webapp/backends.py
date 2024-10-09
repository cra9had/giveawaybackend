from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication

from .models import TelegramUser


class TelegramAuthBackend(BaseAuthentication):
    """Telegram Authentication"""

    def authenticate(self, request):
        telegram_id = request.data.get('telegram_id')
        chat_id = request.data.get('chat_id')

        if not telegram_id or not chat_id:
            return None

        try:
            telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
            if telegram_user.chat_id == chat_id:
                return telegram_user
            raise AuthenticationFailed("Chat id is incorrect")

        except TelegramUser.DoesNotExist:
            raise AuthenticationFailed("Telegram user not found")

    def get_user(self, user_id) -> TelegramUser | None:
        try:
            return TelegramUser.objects.get(pk=user_id)
        except TelegramUser.DoesNotExist:
            return None
