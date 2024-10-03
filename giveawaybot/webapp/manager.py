from django.contrib.auth.base_user import BaseUserManager


class TelegramUserManager(BaseUserManager):
    """Telegram User Manager"""

    def create_user(self, telegram_id, chat_id, password=None, **extra_fields):
        if not (telegram_id and chat_id):
            raise ValueError("You must specify both telegram_id and chat_id to proceed")

        telegram_user = self.model(telegram_id=telegram_id, **extra_fields)
        telegram_user.set_chat_id(chat_id)
        if password:
            telegram_user.set_password(password)
        telegram_user.save(using=self._db)
        return telegram_user

    def create_superuser(self, telegram_id, chat_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(telegram_id, chat_id, password=password, **extra_fields)
