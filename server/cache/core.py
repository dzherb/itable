from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import cast, overload, Protocol

from django.conf import settings

from cache.redis import RedisCache


class Cache(Protocol):
    async def get[T](self, key: str) -> T | None: ...

    @overload
    async def set[T](self, key: str, value: T, *, ttl: timedelta) -> None: ...

    @overload
    async def set[T](
        self,
        key: str,
        value: T,
        *,
        expires_at: datetime,
    ) -> None: ...


cache: Cache = RedisCache(url=settings.REDIS_URL)


@asynccontextmanager
async def connect_cache_storage() -> AsyncIterator[None]:
    try:
        yield
    finally:
        await cast(RedisCache, cache)._client.aclose()
