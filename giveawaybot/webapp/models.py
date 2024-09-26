from django.db import models
from django.utils.crypto import get_random_string


class TelegramUser(models.Model):
    """Модель пользователя"""
    telegram_id = models.CharField(max_length=128, unique=True)
    is_bot = models.BooleanField(default=False)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    username = models.CharField(max_length=128, null=True, blank=True)
    referral_code = models.CharField(max_length=10, blank=True, null=True)
    referrer = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')
    referral_bonus = models.IntegerField(verbose_name="Количество бонусов от рефералов", default=0)

    def __str__(self):
        return self.username
    def generate_referral_code(self):
        return get_random_string(length=10)

    def register_user(self, telegram_id, first_name, last_name, referrer_code=None):
        user = TelegramUser.objects.create(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            referral_code=self.generate_referral_code()
        )

        if referrer_code:
            try:
                referrer = TelegramUser.objects.get(referral_code=referrer_code)
                user.referrer = referrer
                user.save()

                # Награда для реферера
                referrer.referral_bonus += 1
                referrer.save()

                # Записываем информацию о награде
                ReferralReward.objects.create(user=user, referrer=referrer)
            except TelegramUser.DoesNotExist:
                pass  # Обработка ошибки: реферальный код не найден


class ReferralReward(models.Model):
    """Модель для отслеживания наград за рефералов"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    referrer = models.ForeignKey(TelegramUser, related_name='rewards', on_delete=models.CASCADE)
    reward_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} referred by {self.referrer}"


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
    start_date = models.DateField(verbose_name="Дата начала")
    winners_count = models.IntegerField(verbose_name="Количество призовых мест")
    prize = models.ForeignKey(Prize, verbose_name="Приз", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    """Модель билета для розыгрыша"""
    giveaway = models.ForeignKey(GiveAway, verbose_name="Розыгрыш", on_delete=models.CASCADE)
    participant = models.ForeignKey(TelegramUser, verbose_name="Участник", on_delete=models.CASCADE)
    create_date = models.DateField(verbose_name="Дата создания")
    number_ticket = models.IntegerField(verbose_name="Номер тикета")
