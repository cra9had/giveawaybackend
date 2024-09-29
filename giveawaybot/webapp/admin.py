from django.contrib import admin

from .models import TelegramUser, GiveAway, Ticket


@admin.register(TelegramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "telegram_id",
        "is_bot",
        "first_name",
        "first_name",
        "last_name",
        "username"
    )
    search_fields = ("id",)
    list_filter = ("id",)


@admin.register(GiveAway)
class GiveAwayAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "image",
        "create_date",
        "end_datetime",
        "winners_count",
        "is_referral_system",
        "referral_invites_count",
    )
    search_fields = ("id",)
    list_filter = ("id",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "giveaway",
        "participant",
        "create_date",
        "number_ticket",
    )
    search_fields = ("id",)
    list_filter = ("id",)
