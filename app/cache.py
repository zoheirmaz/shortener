import functools

import redis as redis_lib

from app.redis_client import redis_client


def url_cache(ttl: int = 3600):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, code: str):
            key = f"url:code:{code}"
            try:
                cached = redis_client.get(key)
                if cached is not None:
                    from app.models import URLMap

                    return URLMap(code=code, long_url=cached)
            except redis_lib.RedisError:
                pass

            result = func(self, code)
            if result is not None:
                try:
                    redis_client.setex(key, ttl, result.long_url)
                except redis_lib.RedisError:
                    pass
            return result

        return wrapper

    return decorator
