from app.celery_app import celery_app
from app.config import settings
from app.database import SessionLocal
from app.repositories.sqlalchemy_code_pool_repository import SQLAlchemyCodePoolRepository


@celery_app.task
def seed_code_pool_task() -> None:
    db = SessionLocal()
    try:
        repository = SQLAlchemyCodePoolRepository(session=db)
        repository.seed_code_pool(target_available=settings.code_pool_target_available)
    finally:
        db.close()


@celery_app.task
def release_stale_reserved_codes_task() -> None:
    db = SessionLocal()
    try:
        repository = SQLAlchemyCodePoolRepository(session=db)
        repository.release_stale_reserved_codes(reserved_timeout_seconds=settings.reserved_code_timeout_seconds)
    finally:
        db.close()
