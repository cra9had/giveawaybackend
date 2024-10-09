from django.core.management import BaseCommand
from webapp.models import TelegramUser


class Command(BaseCommand):
    help = "Create a superuser for the Telegram user model."

    def handle(self, *args, **kwargs):
        telegram_id = 77777779
        password = "root"

        try:
            TelegramUser.objects.create_superuser(
                telegram_id=telegram_id,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                f"Суперпользователь успешно создан.\nДанные для входа\nLogin: {telegram_id}\nPassword: {password}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при создании суперпользователя: {e}"))
