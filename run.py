import os
import logging
from dotenv import load_dotenv
from app import create_app

load_dotenv()
logger = logging.getLogger(__name__)

port = os.getenv('FLASK_PORT')

app = create_app()

if __name__ == "__main__":
    logger.info(f"Запуск сервера Flask на порту {port}")
    app.run(debug=True, host='0.0.0.0', port=int(port))
