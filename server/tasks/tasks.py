import logging

from services.exchange.synchronization.imoex_synchronizer import (
    IMOEXSynchronizer,
)

logger = logging.getLogger(__name__)


async def imoex_synchronization() -> None:
    await IMOEXSynchronizer().synchronize()
