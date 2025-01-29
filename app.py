import logging
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import td

load_dotenv()

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Кастомные исключения


class DataValidationError(Exception):
    """Ошибка валидации данных"""


class AuthenticationError(Exception):
    """Ошибка авторизации"""


@app.errorhandler(DataValidationError)
def handle_data_validation_error(e):
    logger.error(f"Ошибка валидации данных: {e}")
    return jsonify({"error": str(e)}), 400


@app.errorhandler(AuthenticationError)
def handle_authentication_error(e):
    logger.error(f"Ошибка авторизации: {e}")
    return jsonify({"error": str(e)}), 401


@app.errorhandler(Exception)
def handle_general_error(e):
    logger.exception(f"Внутренняя ошибка сервера: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

# Обёртка для логирования входящих данных и ответов


def log_request_response(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Вызов {func.__name__}: {request.json}")
        response = func(*args, **kwargs)
        logger.info(f"Ответ {func.__name__}: {response.get_json()}")
        return response
    return wrapper


@app.route('/getShipmentsByParams', methods=['POST'])
@log_request_response
def get_shipment():
    data = request.json
    if not data or 'auth' not in data or 'receiver_id' not in data:
        raise DataValidationError("auth и receiver_id обязательны")
    auth_data = data['auth']
    receiver_id = data['receiver_id']
    response = td.get_shipments(auth_data, receiver_id)
    return jsonify(response)


@app.route('/getOrdersByParams', methods=['POST'])
@log_request_response
def get_orders_by_params():
    data = request.json
    if not data or 'auth' not in data or 'shipment_id' not in data:
        raise DataValidationError("auth и shipment_id обязательны")
    shipment_id = data['shipment_id']
    auth_data = data['auth']
    orders = td.get_orders(auth_data, shipment_id)
    return jsonify(orders)


@app.route('/getOrdersInfo', methods=['POST'])
@log_request_response
def get_order_info():
    data = request.json
    if not data or 'auth' not in data or 'order_id' not in data:
        raise DataValidationError("auth и order_id обязательны")
    order_id = data['order_id']
    auth_data = data['auth']
    order_info = td.get_order_info(auth_data, order_id)
    return jsonify(order_info)


@app.route('/getOrdersInfoWebshop', methods=['POST'])
@log_request_response
def get_order_info_by_webshop():
    data = request.json
    if not data or 'auth' not in data or 'webshop_number' not in data:
        raise DataValidationError("auth и webshop_number обязательны")
    webshop_number = data['webshop_number']
    auth_data = data['auth']
    order_info = td.get_order_info_by_webshop(auth_data, webshop_number)
    return jsonify(order_info)


@app.route('/getOrdersInfoBarcode', methods=['POST'])
@log_request_response
def get_order_info_by_barcode():
    data = request.json
    if not data or 'auth' not in data or 'barcode' not in data:
        raise DataValidationError("auth и barcode обязательны")
    barcode = data['barcode']
    auth_data = data['auth']
    order_info = td.get_order_info_by_barcode(auth_data, barcode)
    return jsonify(order_info)


@app.route('/setOrdersFinalStatus', methods=['POST'])
@log_request_response
def set_orders_final_status():
    data = request.json
    if not data or 'auth' not in data:
        raise DataValidationError("auth обязателен")
    auth_data = data['auth']
    response = td.set_final_status(auth_data, **data)
    return jsonify(response)


@app.route('/saveScanningResults', methods=['POST'])
@log_request_response
def save_scanning_results():
    data = request.json
    if not data or 'auth' not in data or 'shipment_id' not in data or 'order_ids' not in data:
        raise DataValidationError("auth, shipment_id и order_ids обязательны")
    auth_data = data['auth']
    shipment_id = data['shipment_id']
    order_ids = data['order_ids']
    response = td.save_scanning_results(auth_data, shipment_id, order_ids)
    return jsonify(response)


@app.route('/setOrderProblemStatus', methods=['POST'])
@log_request_response
def set_order_problem_status():
    data = request.json
    if not data or 'auth' not in data or 'webshop_number' not in data or 'problem_status' not in data:
        raise DataValidationError(
            "auth, webshop_number и problem_status обязательны")
    auth_data = data['auth']
    webshop_number = data['webshop_number']
    problem_status = data['problem_status']
    note = data.get('note')
    response = td.set_problem_status(
        auth_data, webshop_number, problem_status, note)
    return jsonify(response)


@app.route('/setOrdersSentToDelivery', methods=['POST'])
@log_request_response
def set_orders_sent_to_delivery():
    data = request.json
    if not data or 'auth' not in data or 'order_id' not in data or 'date_sent_to_delivery' not in data:
        raise DataValidationError(
            "auth, order_id и date_sent_to_delivery обязательны")
    auth_data = data['auth']
    response = td.set_sent_to_delivery(auth_data, **data)
    return jsonify(response)


port = os.getenv('FLASK_PORT')

if __name__ == "__main__":
    logger.info(f"Запуск сервера Flask на порту {port}")
    app.run(debug=True, host='0.0.0.0', port=int(port))
