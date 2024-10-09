from django.contrib.auth.base_user import BaseUserManager


class TelegramUserManager(BaseUserManager):
    def create_user(self, telegram_id, password=None, **extra_fields):
        print(f"{telegram_id=}")
        if not telegram_id:
            raise ValueError('The Telegram ID field must be set')
        user = self.model(telegram_id=telegram_id, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(telegram_id, password, **extra_fields)
