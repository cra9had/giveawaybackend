import string
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
from django.utils import timezone
from datetime import datetime
from django.conf import settings
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

    @property
    def blured_username(self):
        """
        Replaces three characters in the middle of the given string with asterisks (***).

        Args:
            s (str): Input string.

        Returns:
            str: String with three middle characters replaced by ***.
        """
        length = len(self.telegram_username)
        if length <= 3:
            return '*' * length

        middle_start = (length - 3) // 2
        middle_end = middle_start + 3

        return self.telegram_username[:middle_start] + '***' + self.telegram_username[middle_end:]

    def __str__(self):
        return f"Telegram user, id: {self.telegram_id}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class TelegramChannel(models.Model):
    channel_name = models.CharField(verbose_name="Название канала", max_length=256)
    date_created = models.DateTimeField(verbose_name="Дата привязки", auto_now_add=True)
    chat_id = models.BigIntegerField(verbose_name="ID канала")
    owner = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Привязал")

    def __str__(self):
        return self.channel_name

    class Meta:
        verbose_name = "Канал"
        verbose_name_plural = "Привязанные каналы"



class GiveAway(models.Model):
    """Модель розыгрыша"""
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('in_progress', 'В процессе'),
        ('end', 'Закончен'),
    ]

    channel = models.ForeignKey(TelegramChannel, verbose_name="Канал", on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(verbose_name="Название", max_length=100)
    description = models.CharField(verbose_name="Описание", max_length=254)
    image = models.FileField(verbose_name="Изображение", upload_to=settings.SAVE_GIVEAWAY_MEDIA_TO, blank=True, null=True)
    show_media_above_text = models.BooleanField(verbose_name="Показывать изображение перед текстом", default=False)
    create_date = models.DateField(verbose_name="Дата создания", auto_now_add=True)
    message_id = models.BigIntegerField(verbose_name="ID сообщения в канале", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="Время завершения розыгрыша", null=True, blank=True)
    winners_count = models.IntegerField(verbose_name="Количество призовых мест")
    is_referral_system = models.BooleanField(verbose_name="Реферальная система", default=False)
    referral_invites_count = models.IntegerField(verbose_name="Количество приглашений", null=True, blank=True)
    status = models.CharField(verbose_name="Статус", max_length=20, choices=STATUS_CHOICES, default='created')
    logs = models.JSONField(default=list, blank=True)

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

    @property
    def formatted_end_datetime(self):
        utc_plus_5 = timezone.timedelta(hours=5)
        # Convert end_datetime to UTC+5
        local_end_datetime = self.end_datetime + utc_plus_5
        # Format the datetime
        return local_end_datetime.strftime('%H:%M, %d.%m.%Y (Астана)')

    def get_winners(self) -> QuerySet:
        return self.ticket_set.filter(
            is_winner=True,
        ).order_by('position')

    def time_remaining(self):
        return int(self.end_datetime.timestamp()) if self.end_datetime else None

    def add_log(self, log_entry: dict):
        """
        Добавляет лог в конец списка logs и сохраняет модель.
        log_entry должен быть словарём (dict).
        """
        if not isinstance(log_entry, dict):
            raise ValueError(f"log_entry should be type dict, not {type(log_entry)}")

        self.logs.append(log_entry)
        self.save()

    def get_total_participants(self):
        return (
            Ticket.objects.filter(giveaway=self)
            .values('participant')  # Group by participant
            .distinct()  # Ensure distinct participants
            .count()
        )

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
        """Создание нового билета с уникальным номером"""
        while True:
            new_ticket = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if not Ticket.objects.filter(number_ticket=new_ticket, giveaway=self.giveaway).exists():
                return new_ticket

    def get_ref_param(self):
        from aiogram.utils.deep_linking import create_deep_link

        # TODO: Deep link creation
        return create_deep_link(username="",
                                payload=f'{self.participant.telegram_id}_{self.giveaway.pk}',
                                link_type="start",
                                encode=True)

    def save(self, *args, **kwargs):
        if not self.pk:    # Object created
            self.number_ticket = self.create_ticket()
        super(Ticket, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Ticket {self.number_ticket} for {self.participant.telegram_username}"

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
