from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.interfaces import CodePoolRepository, URLRepository
from app.repositories.sqlalchemy_code_pool_repository import SQLAlchemyCodePoolRepository
from app.repositories.sqlalchemy_url_repository import SQLAlchemyURLRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_url_repository(db: Session = Depends(get_db)) -> URLRepository:
    return SQLAlchemyURLRepository(session=db)


def get_code_pool_repository(db: Session = Depends(get_db)) -> CodePoolRepository:
    return SQLAlchemyCodePoolRepository(session=db)
