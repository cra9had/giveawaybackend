from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import TelegramUser, GiveAway, Ticket
from .serializers import TelegramUserSerializer, GiveAwaySerializer, TicketSerializer

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
        """Метод для присоединения участника к розыгрышу и выдачи билета"""
        giveaway = get_object_or_404(GiveAway, id=giveaway_id)
        participant_id = request.data.get("participant_id")
        participant = get_object_or_404(TelegramUser, id=participant_id)

        existing_ticket = Ticket.objects.filter(giveaway=giveaway, participant=participant).first()
        if existing_ticket:
            return Response({"error": "Участник уже присоединился к этому розыгрышу."},
                            status=status.HTTP_400_BAD_REQUEST)

        ticket = Ticket.create_ticket(giveaway=giveaway, participant=participant)
        return Response({"ticket_number": ticket.number_ticket}, status=status.HTTP_201_CREATED)
