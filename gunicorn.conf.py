import multiprocessing
import os
from dotenv import load_dotenv

load_dotenv()

port = os.getenv('FLASK_PORT')

bind = f"0.0.0.0:{port}"
workers = 4
timeout = 600

# Логи
loglevel = "info"
errorlog = "-"  # Логи ошибок выводятся в stderr
accesslog = "-"  # Логи доступа выводятся в stdout
capture_output = True  # Перехватывать вывод stdout/stderr из приложения
