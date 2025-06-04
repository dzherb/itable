from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tasks import tasks

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def run_background_tasks() -> AsyncIterator[None]:
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
