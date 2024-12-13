from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import TelegramUser, GiveAway, Ticket


class TelegramUserSerializer(serializers.Serializer):
    """Сериализатор для модели TelegramUser"""

    def validate(self, _):
        data = self.context.get('request').data
        hash = data.get("hash")
        user = data.get("user", {})
        auth_date = data.get("auth_date")
        telegram_id = user.get("id")

        if not hash:
            raise serializers.ValidationError("Authentication failed")
        # TODO: remove creation. 400 bad request
        try:
            user, created = TelegramUser.objects.get_or_create(telegram_id=telegram_id)
            token, created = Token.objects.get_or_create(user=user)
        except Exception as e:
            raise serializers.ValidationError(f"User creation or retrieval failed, {e}")

        return {
            "token": str(token),
        }


class ParticipantSerializer(serializers.ModelSerializer):
    telegram_username = serializers.SerializerMethodField()
    class Meta:
        model = TelegramUser
        fields = ("telegram_username", "first_name")

    def get_telegram_username(self, obj):
        return obj.blured_username


class TicketSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ticket"""
    create_date = serializers.DateTimeField(format="%d.%m.%Y, %H:%M")
    participant_username = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ("giveaway", "participant_username", "create_date", "number_ticket", "is_winner", "position")

    def get_participant_username(self, obj):
        # Safely retrieve `username` from the related `participant`
        return obj.participant.blured_username if obj.participant else None


class GiveAwaySerializer(serializers.ModelSerializer):
    """Сериализатор для модели GiveAway"""
    invite_link = serializers.SerializerMethodField()
    already_joined = serializers.SerializerMethodField()
    is_winner = serializers.SerializerMethodField()
    total_participants = serializers.SerializerMethodField()
    tickets = TicketSerializer(many=True, read_only=True)
    winners_tickets = TicketSerializer(many=True, read_only=True)
    chat_id = serializers.SerializerMethodField()
    end_datetime = serializers.DateTimeField(format="%d.%m.%Y, %H:%M")

    class Meta:
        model = GiveAway
        fields = (
            "id",
            "chat_id",
            "title",
            "description",
            "image",
            "create_date",
            "end_datetime",
            "winners_count",
            "status",
            "is_referral_system",
            "referral_invites_count",
            "invite_link",
            "terms_of_participation",
            "already_joined",
            "time_remaining",
            "tickets",
            "winners_tickets",
            "is_winner",
            "total_participants",
            "logs",
        )

    def validate(self, data):
        # Проверяем, выбрана ли реферальная система
        if data.get('is_referral_system') and data.get('referral_invites_count') is None:
            raise serializers.ValidationError(
                "Выберите количество друзей, которое должен "
                "пригласить участник для получения билета розыгрыша."
            )
        return data

    def get_chat_id(self, obj) -> int:
        return obj.channel.chat_id

    def get_total_participants(self, obj) -> int:
        return obj.get_total_participants()

    def get_is_winner(self, obj) -> bool:
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        return Ticket.objects.filter(giveaway=obj, participant=user, is_winner=True).exists()

    def get_already_joined(self, obj) -> bool:
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        ticket = Ticket.objects.filter(giveaway=obj, participant=user).first()
        return ticket is not None

    def get_invite_link(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        # Примерный вид сформированной ссылки на созданный розыгрыш
        return request.build_absolute_uri(f"/giveaways/{obj.pk}/")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            user = request.user
            tickets = Ticket.objects.filter(giveaway=instance, participant=user)
            winners_tickets = Ticket.objects.filter(giveaway=instance, is_winner=True)
            representation['tickets'] = TicketSerializer(tickets, many=True).data
            representation['winners_tickets'] = TicketSerializer(winners_tickets, many=True).data
        return representation
