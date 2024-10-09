from django.contrib.auth.base_user import BaseUserManager


class TelegramUserManager(BaseUserManager):
    """Telegram User Manager"""

    use_in_migrations = True

    def create_user(self, telegram_id: int, username=None, **extra_fields):

        extra_fields.setdefault("is_active", True)

        if username is None:
            username = str(telegram_id)

        telegram_user = self.model(
            telegram_id=telegram_id,
            username=username,
            **extra_fields
        )
        telegram_user.save(using=self._db)
        return telegram_user

    def create_superuser(self, telegram_id: int, password: str, username=None, **extra_fields):

        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен быть is_superuser=True.")

        user = self.create_user(
            telegram_id=telegram_id,
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
