from faker import Faker

from src.server.server import app


fake = Faker()


def create_fake_user() -> dict:
    """Метод генерирует фейковые данные пользователя для тестов"""

    fake_name = fake.name().split()
    fake_email = fake.text().split()[0].lower()
    response = {
        "first_name": fake_name[0],
        "last_name": fake_name[1],
        "email": f"{fake_email}@gmail.com"
    }

    return response


class TestAPI:
    """Класс тестирования микросервиса"""

    def setup(self):
        app.testing = True
        self.client = app.test_client()

    def test_start(self):
        """Метод тестирования функции начала работы с сервисом"""

        response = self.client.get('/api/start/')
        assert response.status_code == 200

    def test_show_all_users(self):
        """Метод тестирования функции просмотра всех пользователей"""

        response = self.client.get('/api/show_all_users/')
        assert response.status_code == 200

    def test_create_user(self):
        """Метод тестирования функции создания пользователя"""

        fake_user = create_fake_user()
        response = self.client.post('/api/create_user/', json=fake_user)
        assert response.status_code == 200

    def test_money_transfer(self):
        """Метод тестирования функции пополнения баланса пользователя
        с ответом статус кода 400"""

        values = [['', ''], ['a', ''], ['', 'a'], ['a', 'a'], ['1', 'a'],
                  ['a', '1'], ['', '1'], ['1', ''], ['1', '-100']]

        for user_id, amount_money in values:
            data = {
                "action": "money_transfer",
                "id": user_id,
                "amount_money": amount_money
            }
            response = self.client.post('/api/money_transfer/', json=data)
            assert response.status_code == 400

    def test_write_off_money(self):
        """Метод тестирования функции списания баланса пользователя
        с ответом статус кода 400"""

        values = [['', ''], ['a', ''], ['', 'a'], ['a', 'a'], ['1', 'a'],
                  ['a', '1'], ['', '1'], ['1', ''], ['1', '-100']]

        for user_id, amount_money in values:
            data = {
                "action": "write_off_money",
                "id": user_id,
                "amount_money": amount_money
            }
            response = self.client.post('/api/write_off_money/', json=data)
            assert response.status_code == 400

    def test_money_transaction(self):
        """Метод тестирования функции перевода средств с баланса одного
         пользователя на баланс другого с ответом статус кода 400"""

        values = [['', '', ''], ['a', '', ''], ['', 'a', ''], ['', '', 'a'],
                  ['a', 'a', ''], ['a', '', 'a'], ['', 'a', 'a'],
                  ['1', '2', 'a'], ['1', '2', '-100'], ['1', 'a', '100'],
                  ['1', '1', '100']]

        for id_from, id_to, amount_money in values:
            data = {
                "action": "money_transaction",
                "id_from": id_from,
                "id_to": id_to,
                "amount_money": amount_money
            }
            response = self.client.post('/api/money_transaction/', json=data)
            assert response.status_code == 400

    def test_show_balance(self):
        """Метод тестирования функции просмотра баланса пользователя
        с ответом статус кода 400"""

        first_values = ['', 'a']
        second_values = [['', ''], ['a', ''], ['a', 'a'], ['1', 'a'], ['1', '1']]

        for user_id in first_values:
            data = {
                "id": user_id
            }
            response = self.client.post('/api/money_transaction/', json=data)
            assert response.status_code == 400

        for user_id, currency in second_values:
            data = {
                "id": user_id,
                "currency": currency
            }
            response = self.client.post('/api/money_transaction/', json=data)
            assert response.status_code == 400

    def test_history_transactions(self):
        """Метод тестирования функции просмотра истории транзакций пользователя
        с ответом статус кода 400"""

        first_values = ['', 'a']

        for user_id in first_values:
            data = {
                "id": user_id
            }
            response = self.client.post('/api/history_transactions/', json=data)
            assert response.status_code == 400
