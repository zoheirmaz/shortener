from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cache import url_cache
from app.config import settings
from app.models import URLMap
from app.repositories.interfaces import URLRepository


class SQLAlchemyURLRepository(URLRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_long_url(self, long_url: str) -> URLMap | None:
        return self._session.scalar(select(URLMap).where(URLMap.long_url == long_url))

    @url_cache(ttl=settings.cache_ttl_seconds)
    def get_by_code(self, code: str) -> URLMap | None:
        return self._session.scalar(select(URLMap).where(URLMap.code == code))

    def create(self, code: str, long_url: str) -> URLMap:
        record = URLMap(code=code, long_url=long_url)
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record
