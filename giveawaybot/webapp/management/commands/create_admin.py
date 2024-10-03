from django.core.management import BaseCommand
from webapp.models import TelegramUser


class Command(BaseCommand):
    help = "Create user with admin permissions for project development."

    def handle(self, *args, **kwargs):
        try:
            TelegramUser.objects.create_superuser(
                telegram_id="admin@give.local",
                chat_id="2",
                password="root"
            )
            print("Superuser Created Successfully")
        except Exception as err:
            print(err)
