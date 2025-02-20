from typing import final, override

import aiohttp

from exchange.exchange.stock_markets.moex.iss_client import (
    ISSClientFactory,
    ISSClientFactoryImpl,
)
from exchange.exchange.synchronization.index_providers import (
    IndexProviderProtocol,
    SecurityWeightDict,
)


@final
class IMOEXProvider(IndexProviderProtocol):
    def __init__(self, *, client_factory: ISSClientFactory | None = None):
        self._client_factory = client_factory or ISSClientFactoryImpl()
        self._session = None
        self._result: list[SecurityWeightDict] = []

    @override
    async def get_index_content(self) -> list[SecurityWeightDict]:
        async with aiohttp.ClientSession() as session:
            self._session = session
            await self._collect_weights()

        return self._result

    async def _collect_weights(self):
        resource = (
            '/statistics/engines/stock/markets/index/analytics/IMOEX.json'
        )
        client = self._client_factory.get_client(
            session=self._session,
            resource=resource,
            arguments={'limit': 100},
        )
        response = await client.get()
        for security in response['analytics']:
            self._result.append(
                {
                    'ticker': security['ticker'],
                    'weight': security['weight'],
                },
            )
