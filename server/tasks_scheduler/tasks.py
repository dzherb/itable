from exchange.exchange.synchronization.imoex_synchronizer import (
    IMOEXSynchronizer,
)


async def imoex_synchronization():
    await IMOEXSynchronizer().synchronize()
