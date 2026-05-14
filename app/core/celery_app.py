from celery import Celery
from app.core.config import settings 

# Usar la URL de settings, que ya tiene la lógica de entorno
REDIS_URL = settings.REDIS_URL 

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)