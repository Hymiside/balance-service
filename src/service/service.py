import json
import random
import uuid

import requests

from src.db import database


def money_transfer(data: dict) -> dict and bool:
    """Метод логики зачисления средств на счёт пользователя"""

    if len(data) == 3 and "action" in data and "id" in data and \
            "amount_money" in data:

        try:
            action = data["action"]
            user_id = int(data["id"])
            money = int(data["amount_money"])
        except ValueError:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        if money <= 0:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        check_user = database.get_check_user(user_id)
        if not check_user:
            response = {"error": "Такого пользователя не существует."}
            return response, True

        status = database.to_money_transfer(action, user_id, money)
        if status:
            response = {"ok": "Средства успешно зачислены на счет."}
            return response, False

        response = {"error": "Ошибка при пополнении."}
        return response, True

    response = {"error": "Некорректный формат запроса."}
    return response, True


def write_off_money(data: dict) -> dict and bool:
    """Метод логики списания средств со счета пользователя"""

    if len(data) == 3 and "action" in data and "id" in data and \
            "amount_money" in data:

        try:
            action = data["action"]
            user_id = int(data["id"])
            money = int(data["amount_money"])
        except ValueError:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        if money <= 0:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        check_user = database.get_check_user(user_id)
        if not check_user:
            response = {"error": "Такого пользователя не существует."}
            return response, True

        balance = database.get_balance(user_id)

        if balance < money:
            response = {"error": "Недостаточно средств."}
            return response, True

        if not balance:
            response = {"error": "Ошибка при проверке баланса."}
            return response, True

        new_balance = balance - money
        status = database.to_write_off_money(action, user_id, new_balance, money)

        if not status:
            response = {"error": "Ошибка при списании средств."}
            return response, True
        response = {"ok": "Списание средств прошло успешно."}
        return response, False

    response = {"error": "Некорректный формат запроса."}
    return response, True


def money_transaction(data: dict) -> json:
    """Метод логики перевода средств со счета на счет"""

    if len(data) == 4 and "action" in data and "id_from" in data and \
            "id_to" in data and "amount_money" in data:

        try:
            action = data["action"]
            user_id_from = int(data["id_from"])
            user_id_to = int(data["id_to"])
            money = int(data["amount_money"])
        except ValueError:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        if user_id_from == user_id_to:
            response = {"error": "Вы указали одинаковые id пользователей."}
            return response, True

        if money <= 0:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        check_user_from = database.get_check_user(user_id_from)
        check_user_to = database.get_check_user(user_id_to)
        if not check_user_from or not check_user_to:
            response = {"error": "Такого пользователя не существует."}
            return response, True

        balance = database.get_balance(user_id_from)
        if not balance and balance != 0:
            response = {"error": "Ошибка при проверке баланса."}
            return response, True

        if balance <= money:
            response = {"error": "Недостаточно средств."}
            return response, True

        new_balance = balance - money
        status = database.to_money_transaction(action, user_id_from, user_id_to,
                                               money, new_balance)
        if not status:
            response = {"error": "Ошибка при переводе средств."}
            return response, True
        response = {"ok": "Перевод средств прошел успешно."}
        return response, False

    response = {"error": "Некорректный формат запроса."}
    return response, True


def show_balance(data: dict) -> dict and bool:
    """Метод логики просмотра баланса пользователя"""

    if (len(data) == 1 or len(data) == 2) and "id" in data:

        try:
            user_id = int(data["id"])
        except ValueError:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        check_user = database.get_check_user(user_id)
        if not check_user:
            response = {"error": "Такого пользователя не существует."}
            return response, True

        balance_rub = database.get_balance(user_id)

        if not balance_rub and balance_rub != 0:
            response = {"error": "Ошибка при проверке баланса."}
            return response, True

        if "currency" in data:
            formatted_balance = currency_translation(balance_rub, data["currency"])
            if not formatted_balance:
                response = {"error": "Невозможно отобразить баланс в данной валюте."}
                return response, True

            response = {"ok": f"Баланс: {formatted_balance} {data['currency']}"}
            return response, False
        response = {"ok": f"Баланс: {balance_rub} RUB"}
        return response, False

    response = {"error": "Некорректный формат запроса."}
    return response, True


def currency_translation(balance: int, currency: str) -> bool or int:
    """Метод конвертации баланса из рублей в указанную валюту"""

    data_json = \
        requests.get(url="https://www.cbr-xml-daily.ru/latest.js").json()
    exchange_rates = data_json["rates"]

    if currency not in exchange_rates:
        return False
    formatted_balance = balance * exchange_rates[f"{currency}"]
    return round(formatted_balance, 3)


def history_transactions(data: dict) -> dict and bool:
    """Метод просмотра истории транзакций"""

    type_transactions_ru = {
        "money_transfer": "Зачисление средств",
        "money_transaction": "Перевод средств",
        "write_off_money": "Списание средств"
    }

    if len(data) == 1 and "id" in data:

        try:
            user_id = int(data["id"])
        except ValueError:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        check_user = database.get_check_user(user_id)
        if not check_user:
            response = {"error": "Такого пользователя не существует."}
            return response, True

        user_transactions = database.get_user_transactions(user_id)
        if not user_transactions:
            response = {"ok": "Нет данных о транзакциях пользователя."}
            return response, False

        response = {"ok": {}}

        for transaction in user_transactions:
            type_transaction = \
                type_transactions_ru[
                    f'{database.get_type_transaction(transaction[0])}']

            if type_transaction == "Перевод средств":
                response["ok"][
                    f"{user_transactions.index(transaction) + 1}"] \
                    = {
                    "type": type_transaction,
                    "amount_money": transaction[1],
                    "created_at": transaction[2],
                    "user_id_from": transaction[3],
                    "user_id_to": transaction[4]
                }
                continue

            if transaction[3] is None:
                user_id = transaction[4]
            else:
                user_id = transaction[3]

            response["ok"][f"{user_transactions.index(transaction) + 1}"] \
                = {
                "type": type_transaction,
                "amount_money": transaction[1],
                "created_at": transaction[2],
                "user_id": user_id
            }
        return response, False
    response = {"error": "Некорректный формат запроса."}
    return response, True


def start() -> dict and bool:
    """Метод создает 2 пользователей и заполняет таблицу типов транзакций"""

    first_names = ["Артем", "Сергей", "Ян", "Георгий", "Никита", "Григорий"]
    last_names = ["Иванов", "Петров", "Кукушкин", "Чудакин", "Курилов", "Яров"]
    mail_hosts = ["gmail.com", "yandex.ru", "icloud.com", "live.com", "mail.ru"]

    fill_tb_type_transactions = database.to_fill_type_transaction()
    if not fill_tb_type_transactions:
        response = {"error": "Ошибка при заполнении таблицы типов транзакций."}
        return response, True

    for i in range(2):
        email = str(uuid.uuid4())[:8] + "@" + random.choice(mail_hosts)
        to_create_user_profile = database.to_create_user_profile(
            random.choice(first_names),
            random.choice(last_names), email)
        if not to_create_user_profile:
            response = {"error": "Ошибка при создании пользователя."}
            return response, True
    response = {"ok": "API готово к работе. Можете сделать первый запрос."}
    return response, False


def create_user(data: dict) -> dict and bool:
    """Метод создания нового пользователя"""

    if len(data) == 3 and "first_name" in data and \
            "last_name" in data and "email" in data:

        try:
            first_name = data["first_name"]
            last_name = data["last_name"]
            email = data["email"]
        except ValueError:
            response = {"error": "Некорректный формат запроса."}
            return response, True

        status = database.to_create_user_profile(first_name, last_name, email)
        if not status:
            response = {"error": "Ошибка при создании пользователя."}
            return response, True

        response = {"ok": "Пользователь успешно создан."}
        return response, False

    response = {"error": "Некорректный формат запроса."}
    return response, True


def show_all_users() -> dict:
    """Метод для просмотра данных всех пользователей в БД"""

    users = database.get_all_users()
    if not users:
        response = {"ok": "Нет данных о пользователях."}
        return response

    response = {"ok": {}}
    for user in users:
        response["ok"][users.index(user) + 1] = {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "balance": database.get_balance(user[0])
        }
    return response
