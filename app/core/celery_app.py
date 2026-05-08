from celery import Celery

celery = Celery("worker", broker="redis://climai_redis:6379/0")