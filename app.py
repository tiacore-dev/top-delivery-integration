from flask import Flask, request, jsonify
import td
import logging
from datetime import datetime
import pytz

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/getShipmentsByParams', methods=['POST'])
def get_shipment():
    logger.info('Вызывается getShipmentsByParams')
    data = request.json
    auth_data = data['auth']
    id = data['receiver_id']
    response = td.get_shipments(auth_data, id)
    return jsonify(response)

@app.route('/getOrdersByParams', methods=['POST'])
def get_orders_by_params():
    data = request.json
    shipment_id = data['shipment_id']
    auth_data = data['auth']
    orders = td.get_orders(auth_data, shipment_id)
    return jsonify(orders)

@app.route('/getOrdersInfo', methods = ['POST'])
def get_order_info():
    data = request.json
    order_id=data['order_id']
    auth_data = data['auth']
    order_info = td.get_order_info(auth_data, order_id)
    return jsonify(order_info)

@app.route('/setOrdersFinalStatus', methods=['POST'])
def set_orders_final_status():
    data = request.json
    auth_data = data['auth']
    order_id = data['order_id']
    bar_code = data['bar_code']
    work_status = data['work_status']
    # Получаем параметры, если они отсутствуют, будет присвоено значение None или по умолчанию
    deny_type = data.get('deny_type')
    #date_fact_delivery = data.get('date_fact_delivery')
    #date_fact_delivery = datetime.now()
    # Установка временной зоны Москвы
    moscow_tz = pytz.timezone("Europe/Moscow")
    date_fact_delivery = datetime.now(moscow_tz).strftime('%Y-%m-%d')
    payment_type = data.get('payment_type') 
    client_paid = data.get('client_paid')  
    supplier_summary = data.get('supplier_summary')
    delivery_paid = data.get('delivery_paid')
    response = td.set_final_status(auth_data,
                                order_id, 
                                bar_code, 
                                date_fact_delivery, 
                                client_paid, 
                                work_status, 
                                delivery_paid, 
                                supplier_summary,
                                deny_type, 
                                payment_type)
    return jsonify(response)

@app.route('/saveScanningResults', methods=['POST'])
def save_scanning_results():
    data = request.json
    auth_data = data['auth']
    shipment_id = data['shipment_id']
    #order_ids = [order['orderId'] for order in data['order_ids']]
    order_ids=data['order_ids']
    response = td.save_scanning_results(auth_data, shipment_id, order_ids)
    return jsonify(response)

@app.route('/setOrderProblemStatus', methods = ['POST'])
def set_order_problem_status():
    data = request.json
    auth_data = data['auth']
    order_id = data['order_id']
    problem_status = data['problem_status'] # Это json, там два параметра
    note = data['note']
    response = td.set_problem_status(auth_data, order_id, problem_status, note)
    return jsonify(response)


@app.route('/setOrdersSentToDelivery', methods = ['POST'])
def set_orders_sent_to_delivery():
    data = request.json
    auth_data = data['auth']
    order_id = data['order_id'] 
    date_sent_to_delivery = ['date_sent_to_delivery']
    
    delivery_type = data.get('delivery_type')
    service_id = data.get('service_id')
    delivery_params = data.get('delivery_params')
    response = td.set_sent_to_delivery(auth_data, order_id, date_sent_to_delivery, delivery_type, service_id, delivery_params)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
