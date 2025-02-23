from contextlib import asynccontextmanager
import logging
import os

from django.conf import settings
from django.core.asgi import get_asgi_application
import uvicorn

from utils.asgi.middlewares import LifespanMiddleware

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_asgi_application()


@asynccontextmanager
async def tasks_scheduler_lifespan():
    from tasks_scheduler.scheduler import scheduler

    scheduler.start()
    yield
    scheduler.shutdown()


if settings.RUN_BACKGROUND_TASKS:
    application = LifespanMiddleware(
        application,
        lifespan=tasks_scheduler_lifespan,
    )

if __name__ == '__main__':
    config = uvicorn.Config(
        app='asgi:application',
        loop='uvloop',
        lifespan='on',
        timeout_graceful_shutdown=3,
        host='127.0.0.1' if settings.DEBUG else '0.0.0.0',
        port=8000,
        proxy_headers=True,
    )
    server = uvicorn.Server(config)

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info(
            'Keyboard interrupt received, ASGI server has been shut down',
        )
    except:
        logger.critical('ASGI server crashed', exc_info=True)
        raise
