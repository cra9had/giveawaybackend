from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication

from .models import TelegramUser


class TelegramAuthBackend(BaseAuthentication):
    """Telegram Authentication"""

    def authenticate(self, request):
        telegram_id = request.data.get('user', {}).get('id')

        if not telegram_id:
            return None

        try:
            telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
            return telegram_user, None
        except TelegramUser.DoesNotExist:
            return None

    def get_user(self, user_id) -> TelegramUser | None:
        try:
            return TelegramUser.objects.get(pk=user_id)
        except TelegramUser.DoesNotExist:
            return None
