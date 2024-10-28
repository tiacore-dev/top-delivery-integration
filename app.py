from flask import Flask, request, jsonify
import td
import logging


app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/api/getShipmentsByParams', methods=['GET'])
def get_shipment():
    logger.info('Вызывается getShipmentsByParams')
    response = td.get_shipments()
    return jsonify(response)

@app.route('/api/getOrdersByParams', methods=['POST'])
def get_orders_by_params():
    data = request.json
    shipment_id = data['shipment_id']
    orders = td.get_orders(shipment_id)
    return jsonify(orders)

@app.route('/api/getOrsersInfo', methods = ['POST'])
def get_order_info():
    data = request.json
    order_id=data['order_id']
    order_info = td.get_order_info(order_id)
    return jsonify(order_info)

@app.route('/api/setOrdersFinalStatus', methods=['POST'])
def set_orders_final_status():
    data = request.json
    order_id = data['order_id']
    bar_code = data['bar_code']
    status = data['status']
    # Получаем параметры, если они отсутствуют, будет присвоено значение None или по умолчанию
    deny_type = data.get('deny_type')
    date_fact_delivery = data.get('date_fact_delivery')
    payment_type = data.get('payment_type') 
    client_paid = data.get('client_paid')  

    response = td.set_final_status(order_id, bar_code, status, deny_type, date_fact_delivery, payment_type, client_paid)
    return jsonify(response)

@app.route('/api/saveScanningResults', methods=['POST'])
def save_scanning_results():
    data = request.json
    shipment_id = data['shipment_id']
    order_ids = [order['orderId'] for order in data['order_ids']]
    
    response = td.save_scanning_results(shipment_id, order_ids)
    return jsonify(response)

@app.route('/api/setOrderProblemStatus', methods = ['POST'])
def set_order_problem_status():
    data = request.json
    order_id = data['order_id']
    problem_status = data['problem_status'] # Это json, там два параметра
    note = data['note']
    response = td.set_problem_status(order_id, problem_status, note)
    return jsonify(response)


@app.route('/api/setOrdersSentToDelivery', methods = ['POST'])
def set_orders_sent_to_delivery():
    data = request.json
    order_id = data['order_id'] 
    date_sent_to_delivery = ['date_sent_to_delivery']
    
    delivery_type = data.get('delivery_type')
    service_id = data.get('service_id')
    delivery_params = data.get('delivery_params')
    response = td.set_sent_to_delivery(order_id, date_sent_to_delivery, delivery_type, service_id, delivery_params)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
