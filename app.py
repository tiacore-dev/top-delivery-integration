from flask import Flask, request, jsonify
import td
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Кастомные исключения
class DataValidationError(Exception):
    """Ошибка валидации данных"""
    pass

class AuthenticationError(Exception):
    """Ошибка авторизации"""
    pass

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
    logger.error(f"Внутренняя ошибка сервера: {e}")
    return jsonify({"error": "Internal Server Error"}), 500


@app.route('/getShipmentsByParams', methods=['POST'])
def get_shipment():
    try:
        logger.info('Вызывается getShipmentsByParams')
        data = request.json
        if not data or 'auth' not in data or 'receiver_id' not in data:
            raise DataValidationError("auth и receiver_id обязательны")
        auth_data = data['auth']
        receiver_id = data['receiver_id']
        response = td.get_shipments(auth_data, receiver_id)
        return jsonify(response)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке getShipmentsByParams")
        raise e

@app.route('/getOrdersByParams', methods=['POST'])
def get_orders_by_params():
    try:
        data = request.json
        if not data or 'auth' not in data or 'shipment_id' not in data:
            raise DataValidationError("auth и shipment_id обязательны")
        shipment_id = data['shipment_id']
        auth_data = data['auth']
        orders = td.get_orders(auth_data, shipment_id)
        return jsonify(orders)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке getOrdersByParams")
        raise e
    
@app.route('/getOrdersInfo', methods=['POST'])
def get_order_info():
    try:
        data = request.json
        if not data or 'auth' not in data or 'order_id' not in data:
            raise DataValidationError("auth и order_id обязательны")
        order_id = data['order_id']
        auth_data = data['auth']
        order_info = td.get_order_info(auth_data, order_id)
        return jsonify(order_info)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке getOrdersInfo")
        raise e

@app.route('/getOrdersInfoWebshop', methods=['POST'])
def get_order_info_by_webshop():
    try:
        data = request.json
        if not data or 'auth' not in data or 'webshop_number' not in data:
            raise DataValidationError("auth и webshop_number обязательны")
        webshop_number = data['webshop_number']
        auth_data = data['auth']
        order_info = td.get_order_info_by_webshop(auth_data, webshop_number)
        return jsonify(order_info)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке getOrdersInfoWebshop")
        raise e

@app.route('/setOrdersFinalStatus', methods=['POST'])
def set_orders_final_status():
    try:
        data = request.json
        if not data or 'auth' not in data or 'webshop_number' not in data:
            raise DataValidationError("auth и webshop_number обязательны")
        auth_data = data['auth']
        work_status = data.get('work_status')
        webshop_number = data['webshop_number']
        deny_params = data.get('deny_params', None)
        date_fact_delivery = data.get('date_fact_delivery')
        payment_type = data.get('payment_type') 
        client_paid = data.get('client_paid')  
        delivery_paid = data.get('delivery_paid')
        response = td.set_final_status(auth_data, webshop_number, date_fact_delivery, client_paid, work_status, delivery_paid, payment_type, deny_params)
        return jsonify(response)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке setOrdersFinalStatus")
        raise e

@app.route('/saveScanningResults', methods=['POST'])
def save_scanning_results():
    try:
        data = request.json
        if not data or 'auth' not in data or 'shipment_id' not in data or 'order_ids' not in data:
            raise DataValidationError("auth, shipment_id и order_ids обязательны")
        auth_data = data['auth']
        shipment_id = data['shipment_id']
        order_ids = data['order_ids']
        response = td.save_scanning_results(auth_data, shipment_id, order_ids)
        return jsonify(response)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке saveScanningResults")
        raise e

@app.route('/setOrderProblemStatus', methods=['POST'])
def set_order_problem_status():
    try:
        data = request.json
        if not data or 'auth' not in data or 'webshop_number' not in data or 'problem_status' not in data:
            raise DataValidationError("auth, webshop_number и problem_status обязательны")
        auth_data = data['auth']
        webshop_number = data['webshop_number']
        problem_status = data['problem_status']  # Это json, там два параметра
        note = data.get('note')
        response = td.set_problem_status(auth_data, webshop_number, problem_status, note)
        return jsonify(response)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке setOrderProblemStatus")
        raise e

@app.route('/setOrdersSentToDelivery', methods=['POST'])
def set_orders_sent_to_delivery():
    try:
        data = request.json
        if not data or 'auth' not in data or 'order_id' not in data or 'date_sent_to_delivery' not in data:
            raise DataValidationError("auth, order_id и date_sent_to_delivery обязательны")
        auth_data = data['auth']
        order_id = data['order_id'] 
        date_sent_to_delivery = data['date_sent_to_delivery']
        delivery_type = data.get('delivery_type')
        service_id = data.get('service_id')
        delivery_params = data.get('delivery_params')
        response = td.set_sent_to_delivery(auth_data, order_id, date_sent_to_delivery, delivery_type, service_id, delivery_params)
        return jsonify(response)
    except DataValidationError as e:
        raise e
    except Exception as e:
        logger.exception("Ошибка при обработке setOrdersSentToDelivery")
        raise e


port = os.getenv('FLASK_PORT')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=port)
