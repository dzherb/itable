from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tasks_scheduler import tasks

scheduler = AsyncIOScheduler()

scheduler.add_job(
    func=tasks.imoex_synchronization,
    trigger='interval',
    minutes=15,
)
