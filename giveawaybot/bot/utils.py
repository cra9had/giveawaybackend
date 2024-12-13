import base64
import json
from datetime import datetime, timedelta
import pytz
from webapp.models import GiveAway
from aiogram import Bot
from bot.keyboards import get_join_giveaway_keyboard


gmt_plus_5 = pytz.timezone("Etc/GMT-5")


class InvalidJWT(Exception):
    pass


async def start_giveaway(bot: Bot, giveaway: GiveAway):
    from webapp.tasks import start_giveaway as start_giveaway_celery
    # TODO: send image
    me = await bot.get_me()
    message = await bot.send_message(
        chat_id=giveaway.channel.chat_id,
        text=f"""
{giveaway.description}

Участников: <b>{giveaway.get_total_participants()}</b>
Призовых мест: <b>{giveaway.winners_count}</b>
Дата розыгрыша: <b>{giveaway.formatted_end_datetime}</b>
""", reply_markup=get_join_giveaway_keyboard(giveaway.pk, me.username)
    )
    giveaway.message_id = message.message_id
    giveaway.save()
    start_giveaway_celery(giveaway.pk)


def decode_base64url(base64url_str):
    # Добавляем возможные недостающие символы = для корректного декодирования
    padding = '=' * (4 - len(base64url_str) % 4)
    return base64.urlsafe_b64decode(base64url_str + padding)


def is_valid_jwt_format(token: str) -> bool:
    parts = token.split('.')
    if len(parts) != 3:
        return False

    try:
        # Декодируем заголовок и полезную нагрузку
        header = json.loads(decode_base64url(parts[0]).decode('utf-8'))
        payload = json.loads(decode_base64url(parts[1]).decode('utf-8'))

        # Проверка того, что это действительно JWT
        if 'alg' in header and 'HS256' == header['alg']:
            return True
        return False
    except Exception as e:
        print(f"Ошибка при декодировании JWT: {e}")
        return False


def get_current_date_time_string(timedelta_hours: int = 0):

    # Текущее время в GMT+5
    current_time = datetime.now(gmt_plus_5) + timedelta(hours=timedelta_hours)
    formatted_current_time = current_time.strftime("%H:%M %d.%m.%Y")
    return formatted_current_time


def parse_user_datetime(user_input: str) -> datetime | None:
    """
    Парсит строку в формате "15:56 08.12.2024" и возвращает объект datetime в GMT+5.
    :param user_input: Входное сообщение пользователя.
    :return: Объект datetime, если строка валидна, иначе None.
    """
    try:
        # Парсинг строки в datetime
        user_datetime = datetime.strptime(user_input, "%H:%M %d.%m.%Y")
        # Привязываем объект datetime к часовой зоне GMT+5
        user_datetime = gmt_plus_5.localize(user_datetime)
        return user_datetime
    except ValueError:
        return None

def is_valid_future_datetime(user_datetime: datetime) -> bool:
    """
    Проверяет, что введенная дата находится в будущем относительно текущего времени в GMT+5.
    :param user_datetime: Объект datetime, представляющий время, введенное пользователем.
    :return: True, если дата в будущем, иначе False.
    """
    # Получаем текущее время в GMT+5
    now = datetime.now(gmt_plus_5)
    # Проверяем, что введенная дата больше текущего времени
    return user_datetime > now