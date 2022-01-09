import flask
from flask import Flask, abort, jsonify

from src.service import service


app = Flask(__name__)


@app.route("/api/start/", methods=["GET"])
def start():
    """Метод создает 2 пользователей и заполняет таблицу типов транзакций"""

    response, err = service.start()
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/create_user/", methods=["POST"])
def create_user():
    """Метод создания нового пользователя"""

    data_json = flask.request.json
    response, err = service.create_user(data_json)
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/money_transfer/", methods=["POST"])
def money_transfer():
    """Метод зачисления средств на счёт пользователя"""

    data_json = flask.request.json
    response, err = service.money_transfer(data_json)
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/write_off_money/", methods=["POST"])
def write_off_money():
    """Метод списания средств со счета пользователя"""

    data_json = flask.request.json
    response, err = service.write_off_money(data_json)
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/money_transaction/", methods=["POST"])
def money_transaction():
    """Метод перевода средств со счета на счет"""

    data_json = flask.request.json
    response, err = service.money_transaction(data_json)
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/show_balance/", methods=["POST"])
def show_balance():
    """Метод просмотра баланса пользователя"""

    data_json = flask.request.json
    response, err = service.show_balance(data_json)
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/history_transactions/", methods=["POST"])
def history_transactions():
    """Метод просмотра истории транзакций"""

    data_json = flask.request.json
    response, err = service.history_transactions(data_json)
    if err:
        abort(400, description=response["error"])
    return jsonify(response)


@app.route("/api/show_all_users/", methods=["GET"])
def show_all_users():
    """Метод для просмотра данных всех пользователей в БД"""

    response = service.show_all_users()
    return jsonify(response)


@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=str(error)), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
