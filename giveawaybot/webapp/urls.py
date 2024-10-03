from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelegramAuthView, TelegramUserViewSet, GiveAwayViewSet, TicketViewSet

router = DefaultRouter()

router.register(r'users', TelegramUserViewSet)
router.register(r'giveaways', GiveAwayViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('auth/telegram/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('', include(router.urls)),
]
