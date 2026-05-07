import os
from celery import Celery
from celery.schedules import crontab

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "url_shortener",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
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
