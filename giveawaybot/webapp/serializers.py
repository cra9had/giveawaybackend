from rest_framework import serializers
from .models import TelegramUser, GiveAway, Ticket


class TelegramUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TelegramUser"""

    class Meta:
        model = TelegramUser
        fields = ("telegram_id", "is_bot", "first_name", "last_name", "username")


class GiveAwaySerializer(serializers.ModelSerializer):
    """Сериализатор для модели GiveAway"""
    invite_link = serializers.SerializerMethodField()

    class Meta:
        model = GiveAway
        fields = (
            "title",
            "description",
            "image",
            "create_date",
            "end_datetime",
            "winners_count",
            "is_referral_system",
            "referral_invites_count",
            "invite_link",
        )

    def validate(self, data):
        # Проверяем, выбрана ли реферальная система
        if data.get('is_referral_system') and data.get('referral_invites_count') is None:
            raise serializers.ValidationError(
                "Выберите количество друзей, которое должен "
                "пригласить участник для получения билета розыгрыша."
            )
        return data

    def get_invite_link(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        # TODO: Примерный вид сформированной ссылки на созданный розыгрыш
        return request.build_absolute_uri(f"/giveaways/{obj.pk}/")


class TicketSerializer(serializers.ModelSerializer):

    """Сериализатор для модели Ticket"""

    class Meta:
        model = Ticket
        fields = ("giveaway", "participant", "create_date", "number_ticket")
