from collections.abc import Callable

from asgiref.sync import sync_to_async
from django.db.transaction import Atomic


class AsyncAtomic(Atomic):
    def __init__(self, using=None, savepoint=True, durable=True):
        super().__init__(using, savepoint, durable)

    __aenter__ = sync_to_async(Atomic.__enter__, thread_sensitive=True)
    __aexit__ = sync_to_async(Atomic.__exit__, thread_sensitive=True)


def aatomic(func: Callable):
    async def wrapper(*args, **kwargs):
        async with AsyncAtomic():
            return await func(*args, **kwargs)

    return wrapper
