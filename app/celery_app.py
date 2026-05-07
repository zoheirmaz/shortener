from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "url_shortener",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "seed-code-pool": {
            "task": "app.tasks.seed_code_pool_task",
            "schedule": crontab(minute=0),
        },
        "release-stale-reserved-codes": {
            "task": "app.tasks.release_stale_reserved_codes_task",
            "schedule": crontab(minute="*/5"),
        },
    },
)
