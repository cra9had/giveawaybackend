from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from .manager import TelegramUserManager


class TelegramUser(AbstractUser):
    """Модель Telegram пользователя"""

    username = None
    USERNAME_FIELD = "telegram_id"
    REQUIRED_FIELDS = []

    objects = TelegramUserManager()

    telegram_id = models.BigIntegerField(unique=True, verbose_name="Телеграм ID")
    telegram_username = models.CharField(max_length=255, verbose_name="телеграм Username", null=True, blank=True)
    first_name = models.CharField(max_length=128, null=True, blank=True, verbose_name="Имя пользователь телеграм")
    jwt_token = models.CharField(max_length=1024, verbose_name="JWT токен lotoclub", null=True, blank=telegram_username)
    is_bot = models.BooleanField(default=False, verbose_name="Бот?")

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

    chat_id = models.BigIntegerField(verbose_name="ID канала")
    title = models.CharField(verbose_name="Название", max_length=100)
    description = models.CharField(verbose_name="Описание", max_length=254)
    image = models.ImageField(verbose_name="Изображение", upload_to="images/%Y/%m/", blank=True, null=True)
    create_date = models.DateField(verbose_name="Дата создания", auto_now_add=True)
    end_datetime = models.DateTimeField(verbose_name="Время завершения розыгрыша")
    winners_count = models.IntegerField(verbose_name="Количество призовых мест")
    is_referral_system = models.BooleanField(verbose_name="Реферальная система", default=False)
    referral_invites_count = models.IntegerField(verbose_name="Количество приглашений", null=True, blank=True)
    status = models.CharField(verbose_name="Статус", max_length=20, choices=STATUS_CHOICES, default='created')
    logs = models.JSONField(default=list)

    terms_of_participation = models.JSONField(verbose_name="Условия для участия", default=dict(
        confirm_phone_required=False,
        confirm_email_required=False,
        deposit=dict(
            required=False,
            starting_period='2024-01-01',
            sum=0
        ),
        bet=dict(
            required=False,
            starting_period='2024-01-01',
            sum=0
        )
    ))

    def time_remaining(self):
        now = timezone.now()
        time_left = self.end_datetime - now

        # Если время истекло
        if time_left.total_seconds() <= 0:
            return "00:00:00"

        # Преобразуем разницу во времени
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def add_log(self, log_entry: dict):
        """
        Добавляет лог в конец списка logs и сохраняет модель.
        log_entry должен быть словарём (dict).
        """
        if not isinstance(log_entry, dict):
            raise ValueError(f"log_entry should be type dict, not {type(log_entry)}")

        self.logs.append(log_entry)
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"


class Ticket(models.Model):
    """Модель билета для розыгрыша"""
    giveaway = models.ForeignKey(GiveAway, verbose_name="Розыгрыш", on_delete=models.CASCADE)
    participant = models.ForeignKey(TelegramUser, verbose_name="Участник", on_delete=models.CASCADE)
    create_date = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    number_ticket = models.CharField(verbose_name="Номер тикета", max_length=64, null=True)
    is_winner = models.BooleanField(verbose_name="Победил", default=False)
    position = models.IntegerField(verbose_name="Позиция", blank=True, null=True)

    def create_ticket(self):
        """Создание нового билета"""
        return "!23"


    def save(self, *args, **kwargs):
        if not self.pk:    # Object created
            self.number_ticket = self.create_ticket()
        super(Ticket, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Ticket {self.number_ticket} for {self.participant.telegram_username}"

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
