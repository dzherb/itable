from collections.abc import Callable, Coroutine
import typing

from asgiref.sync import sync_to_async
from django.db.transaction import Atomic


class AsyncAtomic(Atomic):
    def __init__(
        self,
        using: str | None = None,
        savepoint: bool = True,
        durable: bool = True,
    ):
        super().__init__(using, savepoint, durable)

    __aenter__ = sync_to_async(Atomic.__enter__, thread_sensitive=True)
    __aexit__ = sync_to_async(Atomic.__exit__, thread_sensitive=True)


type _AF[**P, T] = Callable[P, Coroutine[typing.Any, typing.Any, T]]


def aatomic[**P, T](func: _AF[P, T]) -> _AF[P, T]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        async with AsyncAtomic():
            return await func(*args, **kwargs)

    return wrapper
