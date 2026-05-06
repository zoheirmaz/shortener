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
