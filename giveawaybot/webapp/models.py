from django.db import models


class TelegramUser(models.Model):
    """Модель пользователя"""
    telegram_id = models.CharField(max_length=128, unique=True)
    is_bot = models.BooleanField(default=False)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    username = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.username


class Prize(models.Model):
    """Модель призов"""
    title = models.CharField(verbose_name="Название", max_length=100)
    description = models.CharField(verbose_name="Описание", max_length=254)
    count = models.IntegerField(verbose_name="Количество")

    def __str__(self):
        return self.title


class GiveAway(models.Model):
    """Модель розыгрыша"""
    title = models.CharField(verbose_name="Название", max_length=100)
    description = models.CharField(verbose_name="Описание", max_length=254)
    image = models.ImageField(verbose_name="Изображение", upload_to="images/%Y/%m/")
    create_date = models.DateField(verbose_name="Дата создания")
    winners_count = models.IntegerField(verbose_name="Количество призовых мест")
    prize = models.ForeignKey(Prize, verbose_name="Приз", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    """Модель тикета пользователя"""
    giveaway = models.ForeignKey(GiveAway, verbose_name="Розыгрыш", on_delete=models.CASCADE)
    participant = models.ForeignKey(TelegramUser, verbose_name="Участник", on_delete=models.CASCADE)
    create_date = models.DateField(verbose_name="Дата создания")
    number_ticket = models.IntegerField(verbose_name="Номер тикета")
