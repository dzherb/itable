from collections.abc import Coroutine
import typing

from asgiref.sync import sync_to_async
from django.db.transaction import Atomic


class AsyncAtomic(Atomic):
    def __init__(self, using=None, savepoint=True, durable=True):
        super().__init__(using, savepoint, durable)

    __aenter__ = sync_to_async(Atomic.__enter__, thread_sensitive=True)
    __aexit__ = sync_to_async(Atomic.__exit__, thread_sensitive=True)


class _AnyAsyncFunc[T](typing.Protocol):
    def __call__(
        self,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Coroutine[typing.Any, typing.Any, T]: ...


def aatomic[T](func: _AnyAsyncFunc[T]) -> _AnyAsyncFunc[T]:
    async def wrapper(*args, **kwargs) -> T:
        async with AsyncAtomic():
            return await func(*args, **kwargs)

    return wrapper
