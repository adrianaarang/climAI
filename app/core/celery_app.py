from celery import Celery
from app.core.config import settings 

# Usar la URL de settings, que ya tiene la lógica de entorno
REDIS_URL = settings.REDIS_URL 

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)
celery_app.conf.beat_schedule = {
    "revisar-telegram-cada-30-segundos": {
        "task": "app.services.telegram_bot.procesar_mensajes_telegram",
        "schedule": 30.0,
    },
}

celery_app.autodiscover_tasks(["app.services"])
