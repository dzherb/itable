from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, AsyncExitStack
import logging
import os
import typing

from asgiref.typing import ASGI3Application
from django.conf import settings
from django.core.asgi import get_asgi_application
import uvicorn

from utils.asgi.middlewares import LifespanMiddleware

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = typing.cast(ASGI3Application, get_asgi_application())


@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    from events.event_bus import EventBus
    from tasks.scheduler import run_background_tasks

    contexts = []

    if settings.RUN_BACKGROUND_TASKS:
        contexts.append(run_background_tasks)

    if settings.HANDLE_EVENTS:
        contexts.append(EventBus.handle_events)

    async with AsyncExitStack() as stack:
        for context in contexts:
            await stack.enter_async_context(context())

        yield


app = LifespanMiddleware(
    app,
    lifespan=lifespan,
)


def main() -> None:
    config = uvicorn.Config(
        app='asgi:app',
        loop='uvloop',
        lifespan='on',
        timeout_graceful_shutdown=10,
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


if __name__ == '__main__':
    main()
