from celery import Celery

from app.core.settings import settings


celery_app = Celery(broker=settings.redis_url)

celery_app.autodiscover_tasks(["app.modules.decision_assistant.tasks"])
