from collections.abc import Iterator
from contextlib import contextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tasks import tasks

scheduler = AsyncIOScheduler()


@contextmanager
def run_background_tasks() -> Iterator[None]:
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()


scheduler.add_job(
    func=tasks.imoex_synchronization,
    trigger='interval',
    minutes=15,
)
