from rest_framework import serializers
from .models import TelegramUser, GiveAway, Ticket


class TelegramUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TelegramUser"""

    class Meta:
        model = TelegramUser
        fields = ("telegram_id", "is_bot", "first_name", "last_name", "username")


class GiveAwaySerializer(serializers.ModelSerializer):
    """Сериализатор для модели GiveAway"""

    class Meta:
        model = GiveAway
        fields = ("title", "description", "image", "create_date", "start_date", "winners_count")


class TicketSerializer(serializers.ModelSerializer):

    """Сериализатор для модели Ticket"""

    class Meta:
        model = Ticket
        fields = ("giveaway", "participant", "create_date", "number_ticket")
