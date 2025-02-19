from exchange.exchange.synchronization.index_providers import (
    IndexProviderProtocol,
)
from exchange.exchange.synchronization.index_providers.imoex import (
    IMOEXProvider,
)
from exchange.exchange.synchronization.index_synchronizer_protocol import (
    IndexSynchronizerProtocol,
)


class IMOEXSynchronizer(IndexSynchronizerProtocol):
    def __init__(self, *, provider: IndexProviderProtocol | None = None):
        self._provider = provider or IMOEXProvider()

    async def synchronize(self): ...
