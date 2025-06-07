import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from enum import auto, Enum
import logging
from typing import ClassVar

from django.conf import settings
from faststream import FastStream
from faststream.nats import NatsBroker
from faststream.types import DecodedMessage, SendableMessage

from events.handlers import router

logger = logging.getLogger(__name__)


class EventBusIsNotRunningError(Exception):
    pass


class Status(Enum):
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()


class EventBus:
    START_TIMEOUT_IN_SECONDS: ClassVar[int] = 10

    status: ClassVar[Status] = Status.STOPPED
    broker: ClassVar[NatsBroker | None] = None

    @classmethod
    async def publish(
        cls,
        message: SendableMessage,
        subject: str,
        headers: dict[str, str] | None = None,
        reply_to: str = '',
    ) -> DecodedMessage | None:
        if cls.status != Status.RUNNING:
            raise EventBusIsNotRunningError()

        assert cls.broker is not None

        return await cls.broker.publish(
            message=message,
            subject=subject,
            headers=headers,
            reply_to=reply_to,
        )

    @classmethod
    @asynccontextmanager
    async def handle_events(cls) -> AsyncIterator[None]:
        if cls.status == Status.RUNNING:
            return

        cls.broker = NatsBroker(settings.NATS_URL, logger=logger)
        cls.broker.include_router(router)

        app = FastStream(cls.broker, logger=logger)

        async with asyncio.timeout(cls.START_TIMEOUT_IN_SECONDS):
            await app.start()

        cls.status = Status.RUNNING

        await cls.publish(None, 'ping')

        try:
            yield
        finally:
            cls.status = Status.STOPPING

            try:
                await app.stop()
            finally:
                logger.info('FastStream app is stopped')
                cls.status = Status.STOPPED
