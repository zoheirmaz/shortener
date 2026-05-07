from abc import ABC, abstractmethod

from app.models import URLMap


class URLRepository(ABC):
    @abstractmethod
    def get_by_long_url(self, long_url: str) -> URLMap | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_code(self, code: str) -> URLMap | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, code: str, long_url: str) -> URLMap:
        raise NotImplementedError


class CodePoolRepository(ABC):
    @abstractmethod
    def allocate_code(self) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def release_reserved_code(self, code: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_used(self, code: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def seed_code_pool(self, target_available: int) -> int:
        raise NotImplementedError
