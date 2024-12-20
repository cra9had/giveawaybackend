from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_join_giveaway_keyboard(giveaway_pk: int, username: str, results: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_text = "Участвовать" if not results else "Результаты"
    button_url = f"https://t.me/{username}?startapp={giveaway_pk}"
    keyboard.add(InlineKeyboardButton(text=button_text, url=button_url))
    return keyboard
