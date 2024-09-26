from django.db import models


class TemporaryUsers(models.Model):
    """Модель пользователя"""
    users = models.JSONField(null=True)

    def __str__(self):
        return self.users


class GiveAway(models.Model):
    """Модель розыгрыша"""
    title = models.CharField(verbose_name="Название", max_length=100)
    status = models.BooleanField(default=False)
    description = models.CharField(verbose_name="Описание", max_length=254)
    owner_id = models.IntegerField()
    winners_count = models.IntegerField(verbose_name="Количество победителей")
    over_date = models.DateField(verbose_name="Дата окончания розыгрыша")

    def __str__(self):
        return self.title
