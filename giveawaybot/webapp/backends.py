from django.contrib.auth import get_user_model
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
            UserModel = get_user_model()
            try:
                telegram_user = TelegramUser.objects.create_user(telegram_id=telegram_id)
                return telegram_user, None
            except Exception as e:
                return None

    def get_user(self, user_id) -> TelegramUser | None:
        try:
            return TelegramUser.objects.get(pk=user_id)
        except TelegramUser.DoesNotExist:
            return None
