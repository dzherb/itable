from collections.abc import Callable

from asgiref.sync import sync_to_async
from django.db.transaction import Atomic


class AsyncAtomicContextManager(Atomic):
    def __init__(self, using=None, savepoint=True, durable=True):
        super().__init__(using, savepoint, durable)

    # thread_sensitive=False ensures that the task runs
    # in a separate thread. It is important because worker
    # tasks running in an asyncio event loop share a thread
    # (and hence a database session). And when code inside
    # the AsyncAtomicContextManager block yields with await,
    # other async code outside that context manager
    # could execute within the same transaction.
    __aenter__ = sync_to_async(Atomic.__enter__, thread_sensitive=True)
    __aexit__ = sync_to_async(Atomic.__exit__, thread_sensitive=True)


def aatomic(func: Callable):
    async def wrapper(*args, **kwargs):
        async with AsyncAtomicContextManager():
            return await func(*args, **kwargs)

    return wrapper
