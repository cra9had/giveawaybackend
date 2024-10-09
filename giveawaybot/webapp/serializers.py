from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TelegramUser, GiveAway, Ticket


class TelegramUserSerializer(serializers.Serializer):
    """Сериализатор для модели TelegramUser"""

    def validate(self, _):
        data = self.context.get('request').data
        hash = data.get("hash")
        user = data.get("user")
        auth_date = data.get("auth_date")
        telegram_id = user.get("id")

        if not hash:
            raise serializers.ValidationError("Authentication failed")
        print(telegram_id)

        try:
            user, created = TelegramUser.objects.get_or_create(telegram_id=telegram_id)
        except Exception as e:
            raise serializers.ValidationError(f"User creation or retrieval failed", {e})

        print(user)
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        print(refresh, access)
        return {
            "refresh_token": str(refresh),
            "access_token": str(access),
        }


class GiveAwaySerializer(serializers.ModelSerializer):
    """Сериализатор для модели GiveAway"""
    invite_link = serializers.SerializerMethodField()

    class Meta:
        model = GiveAway
        fields = (
            "chat_id",
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
