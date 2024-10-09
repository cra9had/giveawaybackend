from django.core.management import BaseCommand
from webapp.models import TelegramUser


class Command(BaseCommand):
    help = "Create a superuser for the Telegram user model."

    def handle(self, *args, **kwargs):
        telegram_id = 7777777
        chat_id = "7777"
        password = "root"

        try:
            TelegramUser.objects.create_superuser(
                telegram_id=telegram_id,
                chat_id=chat_id,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                "Суперпользователь успешно создан.\nДанные для входа\nLogin: 7777777\nPassword: root"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при создании суперпользователя: {e}"))
