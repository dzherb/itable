from datetime import datetime, timedelta
from typing import cast, overload

import redis.asyncio as redis

from cache.common import Cache, PickleMixin, RawValue, Value


class RedisCache(Cache, PickleMixin):
    def __init__(self, url: str):
        self._client = redis.Redis.from_url(url=url)

    @overload
    async def get(
        self,
        key: str,
    ) -> RawValue | None: ...

    @overload
    async def get[T: Value](
        self,
        key: str,
        *,
        as_type: type[T],
    ) -> T | None: ...

    async def get[T: Value](  # type: ignore[misc]
        self,
        key: str,
        *,
        as_type: type[T] | None = None,
    ) -> T | RawValue | None:
        value = await self._client.get(key)

        if as_type is None:
            return cast(RawValue, value)

        return self.deserialize(value, as_type)

    @overload
    async def set(self, key: str, value: Value, *, ttl: timedelta) -> None: ...

    @overload
    async def set(
        self,
        key: str,
        value: Value,
        *,
        expires_at: datetime,
    ) -> None: ...

    @overload
    async def set(
        self,
        key: str,
        value: Value,
    ) -> None: ...

    async def set(
        self,
        key: str,
        value: Value,
        ttl: timedelta | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        await self._client.set(
            key,
            self.serialize(value),
            ex=ttl,
            exat=expires_at,
        )

    async def delete(self, key: str) -> None:
        await self._client.delete(key)
