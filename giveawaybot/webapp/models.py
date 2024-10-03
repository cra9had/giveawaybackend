from django.db import models
from django.contrib.auth.models import AbstractUser

from .manager import TelegramUserManager


class TelegramUser(AbstractUser):
    """Модель Telegram пользователя"""

    username, password, email = None, None, None
    USERNAME_FIELD = "telegram_id"

    REQUIRED_FIELDS = [
        "chat_id",
    ]

    objects = TelegramUserManager()

    telegram_id = models.CharField(max_length=128, unique=True)
    chat_id = models.CharField(max_length=128)
    is_bot = models.BooleanField(default=False)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    def __str__(self):
        return f"Telegram user, id: {self.telegram_id}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class GiveAway(models.Model):
    """Модель розыгрыша"""
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('in_progress', 'В процессе'),
        ('end', 'Закончен'),
    ]

    chat_id = models.CharField(max_length=128)
    title = models.CharField(verbose_name="Название", max_length=100)
    description = models.CharField(verbose_name="Описание", max_length=254)
    image = models.ImageField(verbose_name="Изображение", upload_to="images/%Y/%m/", blank=True, null=True)
    create_date = models.DateField(verbose_name="Дата создания")
    end_datetime = models.DateTimeField(verbose_name="Время завершения розыгрыша")
    winners_count = models.IntegerField(verbose_name="Количество призовых мест")
    is_referral_system = models.BooleanField(verbose_name="Реферальная система", default=False)
    referral_invites_count = models.IntegerField(verbose_name="Количество приглашений", null=True, blank=True)
    status = models.CharField(verbose_name="Статус", max_length=20, choices=STATUS_CHOICES, default='created')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"


class Ticket(models.Model):
    """Модель билета для розыгрыша"""
    giveaway = models.ForeignKey(GiveAway, verbose_name="Розыгрыш", on_delete=models.CASCADE)
    participant = models.ForeignKey(TelegramUser, verbose_name="Участник", on_delete=models.CASCADE)
    create_date = models.DateField(verbose_name="Дата создания")
    number_ticket = models.IntegerField(verbose_name="Номер тикета")

    @classmethod
    def create_ticket(cls, giveaway, participant):
        """Создание нового билета"""
        ticket_number = cls.objects.filter(giveaway=giveaway).count() + 1
        return cls.objects.create(giveaway=giveaway, participant=participant, number_ticket=ticket_number)

    def __str__(self):
        return f"Ticket {self.number_ticket} for {self.participant.username}"

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
