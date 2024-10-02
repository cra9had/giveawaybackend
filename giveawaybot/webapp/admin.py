from typing import Iterable

from django.contrib import admin

from .models import TelegramUser, GiveAway, Ticket


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):

    model = TelegramUser
    list_display = (
        "id",
        "telegram_id",
        "is_bot",
        "first_name",
        "last_name",
        "is_superuser",
        "is_staff",
    )
    search_fields = ("id",)
    list_filter = ("id",)

    def get_readonly_fields(self, request, obj=None) -> Iterable:
        if obj is not None:
            return "chat_id"
        return super(TelegramUserAdmin, self).get_readonly_fields(request, obj)

    fieldsets = (
        (None, {"fields": ("telegram_id", "chat_id", "first_name", "last_name")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "telegram_id",
                    "chat_id",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )


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
