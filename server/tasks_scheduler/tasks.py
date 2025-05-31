from apps.exchange.services.synchronization.imoex_synchronizer import (
    IMOEXSynchronizer,
)


async def imoex_synchronization() -> None:
    await IMOEXSynchronizer().synchronize()
