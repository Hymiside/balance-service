import psycopg2
from psycopg2 import Error

from src import config

HOST = config.HOST
USER_DB = config.USER
PASSWORD = config.PASSWORD
DATABASE = config.DATABASE
PORT = config.PORT


try:
    connection = psycopg2.connect(
        host=HOST,
        user=USER_DB,
        password=PASSWORD,
        database=DATABASE,
        port=PORT
    )
    cursor = connection.cursor()
    cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION "
                   "LEVEL SERIALIZABLE;")
except (Exception, Error) as error:
    print("Ошибка при подключении к базе данных", error)


def to_create_user_profile(first_name: str, last_name: str, email: str) -> bool:
    """Метод создания нового пользовательского профиля для дальнейшего
    взаимодействия с ним"""

    try:
        cursor.execute("INSERT INTO users(first_name, last_name, email) "
                       "VALUES(%s, %s, %s) RETURNING id",
                       (first_name, last_name, email))
        user_id = cursor.fetchone()[0]
        connection.commit()

        cursor.execute("INSERT INTO cash_accounts(user_id) VALUES(%s)",
                       (user_id,))
        connection.commit()
        return True
    except (Exception, Error) as error:
        print("Ошибка при добавлении данных", error)
        return False


def to_fill_type_transaction() -> bool:
    """Метод заполнения таблицы type_transaction для дальнейшего взаимодействия
    с ней"""
    try:
        cursor.execute("SELECT id FROM type_transactions WHERE "
                       "title = 'money_transfer' or title = 'write_off_money' "
                       "or title = 'money_transaction'")
        response = cursor.fetchall()
        if response:
            return True

        cursor.execute("INSERT INTO type_transactions(title) "
                       "VALUES('money_transfer')")
        cursor.execute("INSERT INTO type_transactions(title) "
                       "VALUES('write_off_money')")
        cursor.execute("INSERT INTO type_transactions(title) "
                       "VALUES('money_transaction')")
        connection.commit()
        return True
    except (Exception, Error) as error:
        print("Ошибка при добавлении данных", error)
        return False


def to_money_transfer(action: str, user_id: int, money: int) -> bool:
    """Метод зачисления средств на счет пользователя"""
    try:
        cursor.execute("SELECT balance FROM cash_accounts WHERE user_id = %s",
                       (user_id,))
        balance = cursor.fetchone()[0] + money
        cursor.execute("UPDATE cash_accounts SET balance = %s WHERE "
                       "user_id = %s", (balance, user_id))
        connection.commit()

        cursor.execute("SELECT id FROM type_transactions WHERE title = %s",
                       (action,))
        id_type_transaction = cursor.fetchone()[0]
        cursor.execute("INSERT INTO transactions(type, amount_money, "
                       "user_id_to) VALUES (%s, %s, %s)",
                       (id_type_transaction, money, user_id))
        connection.commit()
        return True
    except (Exception, Error) as error:
        print("Ошибка при зачислении", error)
        return False


def get_balance(user_id: int) -> int or bool:
    """Возвращает баланс пользователя"""

    try:
        cursor.execute("SELECT balance FROM cash_accounts WHERE user_id = %s",
                       (user_id,))
        balance = cursor.fetchone()[0]

        return balance
    except (Exception, Error):
        return False


def to_write_off_money(action: str, user_id: int, new_balance: int, money: int) \
        -> bool:
    """Метод списания средств со счета пользователя"""

    try:
        cursor.execute("UPDATE cash_accounts SET balance = %s WHERE "
                       "user_id = %s", (new_balance, user_id))

        cursor.execute("SELECT id FROM type_transactions WHERE title = %s",
                       (action,))
        id_type_transaction = cursor.fetchone()[0]
        cursor.execute("INSERT INTO transactions(type, amount_money, "
                       "user_id_from) VALUES (%s, %s, %s)",
                       (id_type_transaction, money, user_id))
        connection.commit()
        return True
    except (Exception, Error) as error:
        print("Ошибка при списании", error)
        return False


def to_money_transaction(action: str, user_id_from: int, user_id_to: int,
                         money: int, new_balance: int) -> bool:
    """Метод перевода средств со счета на счет"""

    try:
        cursor.execute("UPDATE cash_accounts SET balance = %s WHERE "
                       "user_id = %s", (new_balance, user_id_from))
        cursor.execute("SELECT balance FROM cash_accounts WHERE user_id = %s",
                       (user_id_to,))
        balance = cursor.fetchone()[0] + money
        cursor.execute("UPDATE cash_accounts SET balance = %s WHERE "
                       "user_id = %s", (balance, user_id_to))
        connection.commit()

        cursor.execute("SELECT id FROM type_transactions WHERE title = %s",
                       (action,))
        id_type_transaction = cursor.fetchone()[0]
        cursor.execute("INSERT INTO transactions(type, amount_money, "
                       "user_id_from, user_id_to) VALUES (%s, %s, %s, %s)",
                       (id_type_transaction, money, user_id_from, user_id_to))
        connection.commit()
        return True
    except (Exception, Error) as error:
        print("Ошибка при переводе", error)
        return False


def get_user_transactions(user_id: int) -> [tuple]:
    """Метод возвращает все транзакции в которых участвовал пользователь"""

    cursor.execute("SELECT type, amount_money, created_at, user_id_from, "
                   "user_id_to FROM transactions WHERE user_id_from = %s "
                   "or user_id_to = %s", (user_id, user_id))
    user_transactions = cursor.fetchall()
    return user_transactions


def get_type_transaction(id_type_transaction: int) -> str:
    """Метод возвращает строковое значение типа транзакции"""

    cursor.execute("SELECT title FROM type_transactions WHERE id = %s",
                   (id_type_transaction,))
    type_transactions = cursor.fetchone()[0]
    return type_transactions


def get_check_user(user_id: int) -> bool:
    """Метод возвращает True, если пользователь существует, False, если не
    существует"""

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    response = cursor.fetchone()

    if not response:
        return False
    return True


def get_all_users() -> [tuple]:
    """Метод возвращает всех пользователей из БД"""

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return users
