from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.interfaces import URLRepository
from app.repositories.sqlalchemy_url_repository import SQLAlchemyURLRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_url_repository(db: Session = Depends(get_db)) -> URLRepository:
    return SQLAlchemyURLRepository(session=db)
