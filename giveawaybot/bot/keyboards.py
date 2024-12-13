from typing import Sequence, Literal, Union, Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.conf import settings
from webapp.models import TelegramChannel


class SetReferralCounter(CallbackData, prefix="set-referral-counter"):
    amount: int


class SelectChannel(CallbackData, prefix="select-channel"):
    channel_pk: int


class EditTermsOfParticipation(CallbackData, prefix="edit-terms-of-participation"):
    name: Literal['deposit', 'bet', 'confirm_email_required', 'confirm_phone_required']


def get_confirm_description_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Редактировать текст", callback_data="edit_description")
    builder.button(text="Продолжить", callback_data="confirm_description")
    return builder.as_markup()


def get_with_media_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="create_giveaway_with_media")
    builder.button(text="Нет", callback_data="create_giveaway_with_out_media")
    builder.adjust(2)
    return builder.as_markup()


def get_preview_giveaway_keyboard(showing_above: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(text="Сменить картинку/GIF/видео", callback_data="change_giveaway_media")
    builder.button(text=f"Переместить медиа {'вверх ↑' if not showing_above else 'вниз ↓'} ",
                   callback_data=f"change_giveaway_media_position")
    builder.button(text="Продолжить", callback_data=f"confirm_giveaway_media")
    builder.adjust(1)
    return builder.as_markup()


def get_use_referral_system_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="use_referral_system")
    builder.button(text="Нет", callback_data="dont_use_referral_system")
    return builder.as_markup()


def referral_counter_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(5):
        builder.button(text=f"{i+1}", callback_data=SetReferralCounter(amount=i+1).pack())
    builder.button(text="Назад", callback_data="cancel_referral_system")
    builder.adjust(5, 1)
    return builder.as_markup()


def choice_channel_keyboard(channels: Sequence[TelegramChannel], selected_channel_pk: int = 0):
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.button(
            text=f"{'☑️ - ' if channel.pk == selected_channel_pk else ''}{channel.channel_name}",
            callback_data=SelectChannel(channel_pk=channel.pk).pack()
        )
    builder.button(text="Добавить канал", callback_data="add_channel")
    builder.button(text="Запустить розыгрыш", callback_data="start_giveaway")
    builder.adjust(*[1 for _ in range(len(channels))], 2)
    return builder.as_markup()


def get_cancel_channel_adding_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Отменить", callback_data="cancel_channel_adding")
    return builder.as_markup()


def get_recheck_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="recheck_confirmed")
    return builder.as_markup()


def get_join_giveaway_keyboard(giveaway_pk: int, username: str, results: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(text="Участвовать" if not results else "Результаты",
                   url=f"https://t.me/{username}?startapp={giveaway_pk}")
    return builder.as_markup()


def get_terms_of_participation_panel_keyboard(terms_of_participation: dict):
    builder = InlineKeyboardBuilder()
    deposit_sum = terms_of_participation.get("deposit").get("sum")
    bet_sum = terms_of_participation.get("bet").get("sum")
    confirm_phone_required = terms_of_participation.get("confirm_phone_required")
    confirm_email_required = terms_of_participation.get("confirm_email_required")

    builder.button(text=f"Пополнил счет на сумму >= {deposit_sum}", callback_data=EditTermsOfParticipation(
        name="deposit"
    ).pack())
    builder.button(text=f"Сделал bet на сумму >= {bet_sum}", callback_data=EditTermsOfParticipation(
        name="bet"
    ).pack())
    builder.button(text=f"Подтвердил номер телефона{' ☑️' if confirm_email_required else ' ❌'}",
                   callback_data=EditTermsOfParticipation(
        name="confirm_email_required"
    ).pack())
    builder.button(text=f"Подтвердил почту{' ☑️' if confirm_phone_required else ' ❌'}",
                   callback_data=EditTermsOfParticipation(
        name="confirm_phone_required",
    ).pack())
    builder.button(text="Подтвердить", callback_data="confirm_terms")
    builder.adjust(1)
    return builder.as_markup()
