from rest_framework import viewsets
from .models import TelegramUser, GiveAway, Ticket
from .serializers import TelegramUserSerializer, GiveAwaySerializer, TicketSerializer
from rest_framework.response import Response
from rest_framework import status

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
