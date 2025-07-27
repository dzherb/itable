from datetime import datetime, timedelta
from typing import cast, overload

import redis.asyncio as redis


class RedisCache:
    def __init__(self, url: str):
        self._client = redis.Redis(url=url)

    async def get[T](self, key: str) -> T | None:
        return cast(T, await self._client.get(key))

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

    async def set[T](
        self,
        key: str,
        value: T,
        ttl: timedelta | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        await self._client.set(key, value, ex=ttl, exat=expires_at)
