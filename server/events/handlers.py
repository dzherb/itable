import logging

from faststream.nats import NatsRouter

logger = logging.getLogger(__name__)

router = NatsRouter()


@router.subscriber('ping')
async def ping() -> None:
    logger.info('Received ping event')
