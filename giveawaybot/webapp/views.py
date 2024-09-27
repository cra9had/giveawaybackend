from rest_framework import viewsets
from .models import TelegramUser, GiveAway, Ticket
from .serializers import TelegramUserSerializer, GiveAwaySerializer, TicketSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import (
    # OpenApiParameter,
    extend_schema,
    extend_schema_view,
)


@extend_schema(
    tags=["TelegramUsers"],
    methods=["GET"],
)
@extend_schema_view(
    post=extend_schema(
        summary="TelegramUsers",
    ),
)
class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    http_method_names = ['get']


@extend_schema(
    tags=["Giveaway"],
    methods=["POST", "GET"],
)
@extend_schema_view(
    post=extend_schema(
        summary="Giveaway",
    ),
)
class GiveAwayViewSet(viewsets.ModelViewSet):
    queryset = GiveAway.objects.all()
    serializer_class = GiveAwaySerializer
    http_method_names = ['get', 'post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    tags=["Ticket"],
    methods=["POST"],
)
@extend_schema_view(
    post=extend_schema(
        summary="Ticket",
    ),
)
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    http_method_names = ['post']

    @action(detail=False, methods=['post'], url_path='join/(?P<giveaway_id>[^/.]+)')
    def join_giveaway(self, request, giveaway_id=None):
        """Метод выдачи билета участнику"""
        try:
            giveaway = GiveAway.objects.get(id=giveaway_id)
            participant_id = request.data.get("participant_id")
            participant = TelegramUser.objects.get(id=participant_id)

            # Проверяем, есть ли уже билет у участника для данного розыгрыша
            existing_ticket = Ticket.objects.filter(giveaway=giveaway, participant=participant).first()
            if existing_ticket:
                return Response({"error": "Participant has already joined this giveaway."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Создаем новый билет
            ticket = Ticket.create_ticket(giveaway=giveaway, participant=participant)
            return Response({"ticket_number": ticket.number_ticket}, status=status.HTTP_201_CREATED)
        except GiveAway.DoesNotExist:
            return Response({"error": "Giveaway not found."}, status=status.HTTP_404_NOT_FOUND)
        except TelegramUser.DoesNotExist:
            return Response({"error": "Participant not found."}, status=status.HTTP_404_NOT_FOUND)

        # TODO: Дорабоать
