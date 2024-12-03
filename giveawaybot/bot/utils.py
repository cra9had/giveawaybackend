import base64
import json


class InvalidJWT(Exception):
    pass


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
