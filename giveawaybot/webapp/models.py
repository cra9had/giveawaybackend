from django.db import models


class TelegramUser(models.Model):
    """Модель пользователя"""
    telegram_id = models.CharField(max_length=128, unique=True)
    is_bot = models.BooleanField(default=False)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"@{self.username}" if self.username else str(self.telegram_id)


class GiveAway(models.Model):
    """Модель розыгрыша"""
    title = models.CharField(verbose_name="Название", max_length=50)
    description = models.CharField(verbose_name="Описание", max_length=2000)
    image = models.ImageField(verbose_name="Изображение", upload_to="images/%Y/%m/", blank=True, null=True)
    create_date = models.DateField(verbose_name="Дата создания", auto_now_add=True)
    end_datetime = models.DateTimeField(verbose_name="Время завершения розыгрыша")
    winners_count = models.IntegerField(verbose_name="Количество призовых мест")
    is_referral_system = models.BooleanField(verbose_name="Реферальная система", default=False)
    referral_invites_count = models.IntegerField(verbose_name="Количество приглашений для нового билета", null=True, blank=True)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    """Модель билета для розыгрыша"""
    giveaway = models.ForeignKey(GiveAway, verbose_name="Розыгрыш", on_delete=models.CASCADE)
    participant = models.ForeignKey(TelegramUser, verbose_name="Участник", on_delete=models.CASCADE)
    create_date = models.DateTimeField(verbose_name="Время создания", auto_now_add=True)
    number_ticket = models.IntegerField(verbose_name="Номер тикета")

    def __str__(self):
        return f"Ticket {self.number_ticket} for {self.participant.username}"

    @classmethod
    def create_ticket(cls, giveaway, participant):
        """Создание нового билета"""
        ticket_number = cls.objects.filter(giveaway=giveaway).count() + 1
        return cls.objects.create(giveaway=giveaway, participant=participant, number_ticket=ticket_number)
