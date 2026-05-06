from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CodePool, URLMap
from app.repositories.interfaces import URLRepository
from app.service import generate_random_code


class SQLAlchemyURLRepository(URLRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_long_url(self, long_url: str) -> URLMap | None:
        return self._session.scalar(select(URLMap).where(URLMap.long_url == long_url))

    def get_by_code(self, code: str) -> URLMap | None:
        return self._session.scalar(select(URLMap).where(URLMap.code == code))

    def create(self, code: str, long_url: str) -> URLMap:
        record = URLMap(code=code, long_url=long_url)
        self._session.add(record)

        code_pool_item = self._session.scalar(select(CodePool).where(CodePool.code == code))
        if code_pool_item:
            code_pool_item.status = "used"
            code_pool_item.used_at = datetime.now(timezone.utc)

        self._session.commit()
        self._session.refresh(record)
        return record

    def allocate_code(self) -> str | None:
        candidate = self._session.scalar(
            select(CodePool)
            .where(CodePool.status == "available")
            .order_by(CodePool.id.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if not candidate:
            return None

        candidate.status = "reserved"
        candidate.reserved_at = datetime.now(timezone.utc)
        self._session.flush()
        return candidate.code

    def release_reserved_code(self, code: str) -> None:
        code_pool_item = self._session.scalar(select(CodePool).where(CodePool.code == code))
        if not code_pool_item:
            return
        code_pool_item.status = "available"
        code_pool_item.reserved_at = None
        code_pool_item.used_at = None
        self._session.commit()

    def seed_code_pool(self, target_available: int) -> int:
        available_count = self._session.scalar(
            select(func.count()).select_from(CodePool).where(CodePool.status == "available")
        )
        if not available_count:
            available_count = 0

        created = 0
        while available_count + created < target_available:
            code = generate_random_code()
            self._session.add(CodePool(code=code, status="available"))
            try:
                self._session.flush()
                created += 1
            except IntegrityError:
                self._session.rollback()
                continue

        self._session.commit()
        return created
