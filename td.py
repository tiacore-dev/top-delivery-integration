import zeep
import requests
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
import hashlib
from zeep.helpers import serialize_object
import os
from dotenv import load_dotenv
import logging
from utils import serialize_dates

load_dotenv()

logger = logging.getLogger(__name__)

# Параметры аутентификации и URL WSDL
wsdl_url = os.getenv('WSDL_URL')  # Подставьте сюда актуальный URL
login_soap = os.getenv('SOAP_LOGIN')
password_soap = os.getenv('SOAP_PASSWORD')

# Настроим сессию с аутентификацией
session = requests.Session()
session.auth = HTTPBasicAuth(login_soap, password_soap)
client = zeep.Client(wsdl=wsdl_url, transport=Transport(session=session))

# 2.1 Получить все отправления заказов, которые ушли со склада ТД, но еще не приняты
def get_shipments(auth_data, id):
    try:
        logger.info("Запуск метода get_shipments")
        response = client.service.getShipmentsByParams(
            auth=auth_data,
            shipmentDirection={'receiverId': id},
            shipmentStatus={'id': '3'}
        )
        logger.info(f"Ответ от get_shipments: {response}")
        shipments = serialize_object(response)
        shipments = serialize_dates(shipments)
        return shipments
    except Exception as e:
        logger.error(f"Ошибка в get_shipments: {e}", exc_info=True)
        return None

# 2.2 Получить список заказов для каждого отправления
def get_orders(auth_data, shipment_id):
    try:
        logger.info(f"Запуск метода get_orders с параметром shipment_id={shipment_id}")
        response = client.service.getOrdersByParams(auth=auth_data, currentShipment=shipment_id)
        logger.info(f"Ответ от get_orders: {response}")
        orders = serialize_object(response)
        orders = serialize_dates(orders)
        return orders
    except Exception as e:
        logger.error(f"Ошибка в get_orders: {e}", exc_info=True)
        return None

# Получить детальную информацию по каждому заказу
def get_order_info(auth_data, order_id):
    try:
        logger.info(f"Запуск метода get_order_info с параметром order_id={order_id}")
        response = client.service.getOrdersInfo(auth=auth_data, order={'orderId': order_id})
        logger.info(f"Ответ от get_order_info: {response}")
        order_info = serialize_object(response)
        order_info = serialize_dates(order_info)
        return order_info
    except Exception as e:
        logger.error(f"Ошибка в get_order_info: {e}", exc_info=True)
        return None

def get_order_id(auth_data, webshop_number):
    try:
        data = get_order_info_by_webshop(auth_data, webshop_number)
        if not data or 'orderInfo' not in data:
            raise ValueError("Данные orderInfo отсутствуют в ответе")
        
        order_info = data.get("orderInfo", [])[0]
        order_identity = order_info.get("orderIdentity")
        
        if not order_identity:
            raise ValueError("Данные orderIdentity отсутствуют в orderInfo")
        
        # Исправлено: правильное имя ключа
        order_id = order_identity['orderId']  
        bar_code = order_identity['barcode']
        
        return order_id, bar_code
    except Exception as e:
        logger.error(f"Ошибка в get_order_id: {e}", exc_info=True)
        return None, None

def get_order_info_by_webshop(auth_data, webshop_number):
    try:
        logger.info(f"Запуск метода get_order_info_by_webshop с параметром webshop_number={webshop_number}")
        order = {"webshopNumber": webshop_number}
        response = client.service.getOrdersByParams(auth=auth_data, orderIdentity=order)
        logger.info(f"Ответ от get_order_info_by_webshop: {response}")
        order_info = serialize_object(response)
        order_info = serialize_dates(order_info)
        return order_info
    except Exception as e:
        logger.error(f"Ошибка в get_order_info_by_webshop: {e}", exc_info=True)
        return None

# 2.3 Передать финальный статус заказа в ТД
def set_final_status(auth_data, webshop_number, date_fact_delivery, client_paid, work_status, delivery_paid, payment_type, deny_params=None):
    try:
        order_id, bar_code = get_order_id(auth_data, webshop_number)
        if not order_id or not bar_code:
            raise ValueError("Не удалось получить order_id или barcode")
        access_code = hashlib.md5(f"{str(order_id)}+{bar_code}".encode()).hexdigest()
        logger.info(f"Запуск метода set_final_status с параметрами order_id={order_id}, workStatus={work_status},")
        final_status_params = {
            "orderIdentity": {
                "orderId": order_id,
                "barcode": bar_code,
                "webshopNumber": webshop_number
            },
            "accessCode": access_code,
            "workStatus": work_status,
            "dateFactDelivery": date_fact_delivery,
            "paymentType": payment_type,
            "clientPaid": client_paid,
            "deliveryPaid": delivery_paid
        }
        if work_status['id'] == "5" and deny_params:
            final_status_params["denyParams"] = deny_params
        response = client.service.setOrdersFinalStatus(
            auth=auth_data, 
            finalStatusParams=[final_status_params]
        )
        logger.info(f"Ответ от set_final_status: {response}")
        return serialize_object(response), 200
    except Exception as e:
        logger.error(f"Ошибка в set_final_status: {e}", exc_info=True)
        return None, 500

# 2.4 Сохранить результат приема на складе
def save_scanning_results(auth_data, shipment_id, orders):
    try:
        logger.info(f"Запуск метода save_scanning_results с параметрами shipment_id={shipment_id}, orders={orders}")
        response = client.service.saveScanningResults(auth=auth_data, shipmentId=shipment_id, orders=orders)
        logger.info(f"Ответ от save_scanning_results: {response}")
        return serialize_object(response)
    except Exception as e:
        logger.error(f"Ошибка в save_scanning_results: {e}", exc_info=True)
        return None

# 2.5 Установить статус проблемности заказу
def set_problem_status(auth_data, order_id, problem_status, note=""):
    try:
        logger.info(f"Запуск метода set_problem_status с параметрами order_id={order_id}, problem_status={problem_status}, note={note}")
        response = client.service.setOrderProblemStatus(auth=auth_data, orderId=order_id, problemStatus=problem_status, note=note)
        logger.info(f"Ответ от set_problem_status: {response}")
        return serialize_object(response)
    except Exception as e:
        logger.error(f"Ошибка в set_problem_status: {e}", exc_info=True)
        return None

# 2.6 Установить статус заказа "выдан на доставку"
def set_sent_to_delivery(auth_data, order_id, date_sent_to_delivery, delivery_type=None, service_id=None, delivery_params=None):
    try:
        logger.info(f"Запуск метода set_sent_to_delivery с параметрами order_id={order_id}, date_sent_to_delivery={date_sent_to_delivery}, delivery_type={delivery_type}, service_id={service_id}, delivery_params={delivery_params}")
        date_sent = date_sent_to_delivery.strftime('%Y-%m-%d %H:%M:%S')
        order_identity = {'orderId': order_id}
        response = client.service.setOrdersSentToDelivery(
            auth=auth_data,
            orderIdentity=order_identity,
            dateSentToDelivery=date_sent,
            deliveryType=delivery_type,
            serviceId=service_id,
            deliveryParams=delivery_params
        )
        logger.info(f"Ответ от set_sent_to_delivery: {response}")
        return serialize_object(response)
    except Exception as e:
        logger.error(f"Ошибка в set_sent_to_delivery: {e}", exc_info=True)
        return None
