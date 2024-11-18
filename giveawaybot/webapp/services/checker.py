import requests
from datetime import datetime


BASE_URL = 'https://loto37.xyz'


# Проверка подтверждения номера телефона
def check_phone_confirmation(jwt):
    url = f"{BASE_URL}/api/jwt/confirmed_phone"
    headers = {'X-JWT': jwt}
    response = requests.get(url, headers=headers)
    return response.json().get('result', False)


# Проверка подтверждения email
def check_email_confirmation(jwt):
    url = f"{BASE_URL}/api/jwt/confirmed_email"
    headers = {'X-JWT': jwt}
    response = requests.get(url, headers=headers)
    return response.json().get('result', False)


# Проверка пополнения на заданную сумму за указанный период
def check_deposit(jwt, currency, start_date, end_date, target_sum):
    url = f"{BASE_URL}/api/jwt/check_deposit"
    headers = {'X-JWT': jwt}
    payload = {
        "currency": currency,
        "from": start_date,
        "to": end_date,
        "sum": target_sum
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get('result', False)


# Проверка ставки на заданную сумму за указанный период
def check_bet(jwt, currency, start_date, end_date, target_sum):
    url = f"{BASE_URL}/api/jwt/check_bet"
    headers = {'X-JWT': jwt}
    payload = {
        "currency": currency,
        "from": start_date,
        "to": end_date,
        "sum": target_sum
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get('result', False)


# Основная функция для проверки условий участия
def check_terms_of_participation(jwt, terms_of_participation, currency="KZT") -> dict:
    # Проверка подтверждения номера телефона, если требуется'
    errors = []
    if terms_of_participation.get('confirm_phone_required', False):
        if not check_phone_confirmation(jwt):
            errors.append("confirm_phone_required")

    # Проверка подтверждения email, если требуется
    if terms_of_participation.get('confirm_email_required', False):
        if not check_email_confirmation(jwt):
            errors.append("confirm_email_required")

    # Проверка депозита, если требуется
    deposit_terms = terms_of_participation.get('deposit', {})
    if deposit_terms.get('required', False):
        deposit_start = deposit_terms.get('starting_period', '2024-01-01')
        deposit_sum = deposit_terms.get('sum', 0)
        today = datetime.now().strftime('%Y-%m-%d')
        if not check_deposit(jwt, currency, deposit_start, today, deposit_sum):
            errors.append("deposit")

    # Проверка ставки, если требуется
    bet_terms = terms_of_participation.get('bet', {})
    if bet_terms.get('required', False):
        bet_start = bet_terms.get('starting_period', '2024-01-01')
        bet_sum = bet_terms.get('sum', 0)
        today = datetime.now().strftime('%Y-%m-%d')
        if not check_bet(jwt, currency, bet_start, today, bet_sum):
            errors.append("bet")

    if not errors:
        # Если все проверки выполнены успешно
        return {"status": True, "errors": None}
    else:
        return {"status": False, "errors": errors}


