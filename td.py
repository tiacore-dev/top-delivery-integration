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
    logger.info("Запуск метода get_shipments")
    response = client.service.getShipmentsByParams(
        auth=auth_data,
        shipmentDirection={'receiverId': id},
        shipmentStatus={'id': '3'}
    )
    logger.info(f"Ответ от get_shipments: {response}")

    # Преобразуем ответ в словарь перед возвратом
    shipments = serialize_object(response)

    # Преобразуем все даты и время в строки
    shipments = serialize_dates(shipments)

    return shipments

# 2.2 Получить список заказов для каждого отправления
def get_orders(auth_data, shipment_id):
    logger.info(f"Запуск метода get_orders с параметром shipment_id={shipment_id}")
    response = client.service.getOrdersByParams(auth=auth_data, currentShipment=shipment_id)
    logger.info(f"Ответ от get_orders: {response}")
    orders = serialize_object(response)
    orders = serialize_dates(orders)
    return orders

# Получить детальную информацию по каждому заказу
def get_order_info(auth_data, order_id):
    logger.info(f"Запуск метода get_order_info с параметром order_id={order_id}")
    response = client.service.getOrdersInfo(auth=auth_data, order={'orderId': order_id})
    logger.info(f"Ответ от get_order_info: {response}")
    order_info = serialize_object(response)
    order_info = serialize_dates(order_info)
    return order_info

# 2.3 Передать финальный статус заказа в ТД
def set_final_status(auth_data, order_id, bar_code, status, deny_type=None, date_fact_delivery=None, payment_type='CARD', client_paid=0):
    access_code = hashlib.md5(f"{order_id}+{bar_code}".encode()).hexdigest()
    logger.info(f"Запуск метода set_final_status с параметрами order_id={order_id}, status={status}, deny_type={deny_type}")
    response = client.service.setOrdersFinalStatus(
        auth=auth_data, 
        orderId=order_id,
        accessCode=access_code,
        workStatus={'name': status},
        denyParams={'type': deny_type} if deny_type else None,
        dateFactDelivery=date_fact_delivery.strftime('%Y-%m-%d') if date_fact_delivery else None,
        paymentType=payment_type,
        clientPaid=client_paid
    )
    logger.info(f"Ответ от set_final_status: {response}")
    return serialize_object(response)

# 2.4 Сохранить результат приема на складе
def save_scanning_results(auth_data, shipment_id, order_ids):
    logger.info(f"Запуск метода save_scanning_results с параметрами shipment_id={shipment_id}, order_ids={order_ids}")
    
    # Формируем словарь для передачи заказов
    orders = [{'orderId': order_id} for order_id in order_ids]
    
    response = client.service.saveScanningResults(auth=auth_data, shipmentId=shipment_id, orders=orders)
    logger.info(f"Ответ от save_scanning_results: {response}")
    
    return serialize_object(response)

# 2.5 Установить статус проблемности заказу
def set_problem_status(auth_data, order_id, problem_status, note=""):
    logger.info(f"Запуск метода set_problem_status с параметрами order_id={order_id}, problem_status={problem_status}, note={note}")
    response = client.service.setOrderProblemStatus(auth=auth_data, orderId=order_id, problemStatus=problem_status, note=note)
    logger.info(f"Ответ от set_problem_status: {response}")
    return serialize_object(response)


# 2.6 Установить статус заказа "выдан на доставку"
def set_sent_to_delivery(auth_data, order_id, date_sent_to_delivery, delivery_type=None, service_id=None, delivery_params=None):
    logger.info(f"Запуск метода set_sent_to_delivery с параметрами order_id={order_id}, date_sent_to_delivery={date_sent_to_delivery}, delivery_type={delivery_type}, service_id={service_id}, delivery_params={delivery_params}")
    
    # Форматируем дату
    date_sent = date_sent_to_delivery.strftime('%Y-%m-%d %H:%M:%S')
    
    # Подготовка параметров для запроса
    order_identity = {
        'orderId': order_id  # Передаем orderId внутри orderIdentity
    }

    # Отправляем запрос
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


