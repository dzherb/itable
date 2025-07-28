from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from django.conf import settings

from cache.common import Cache
from cache.redis import RedisCache

cache: Cache = RedisCache(url=settings.REDIS_URL)


@asynccontextmanager
async def connect_cache_storage() -> AsyncIterator[None]:
    try:
        yield
    finally:
        await cast(RedisCache, cache)._client.aclose()
