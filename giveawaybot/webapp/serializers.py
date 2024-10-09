from rest_framework import serializers
from rest_framework.serializers import ValidationError as SerializerError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ValidationError

from .models import TelegramUser, GiveAway, Ticket


class TelegramUserSerializer(serializers.Serializer):
    """Сериализатор для модели TelegramUser"""

    def validate(self, request):
        data = request.data
        hash = data.get("hash")
        user = data.get("user")
        auth_date = data.get("auth_date")
        telegram_id = user.get("telegram_id")

        if not hash:
            raise serializers.ValidationError("Authentication failed")

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            raise serializers.ValidationError("User not found")

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "refresh_token": str(refresh),
            "access_token": str(access),
        }


# class UserLoginSerializer(serializers.ModelSerializer):
#
#     telegram_id = serializers.CharField(max_length=32, required=True)
#     chat_id = serializers.CharField(required=True, write_only=True, max_length=128)
#
#     def validate(self, attrs):
#         try:
#             user = authenticate(self.context["request"], **attrs)
#             refresh = RefreshToken.for_user(user)
#
#             if api_settings.UPDATE_LAST_LOGIN:
#                 update_last_login(None, user)
#
#             return {
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token)
#             }
#         except ValidationError as error:
#             raise SerializerError(error.message) from error


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
