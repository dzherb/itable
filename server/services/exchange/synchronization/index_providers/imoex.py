import logging
import typing
from typing import final, override

import aiohttp

from services.exchange.stock_markets import BaseMOEX, moex_circuit_breaker
from services.exchange.stock_markets.iss_client import ISSClientFactory
from services.exchange.synchronization.typedefs import (
    IndexProviderProtocol,
    SecurityWeightDict,
)

logger = logging.getLogger('exchange.synchronization')


@final
class IMOEXProvider(BaseMOEX, IndexProviderProtocol):
    def __init__(
        self,
        *,
        client_factory: ISSClientFactory | None = None,
        timeout: aiohttp.ClientTimeout | int | None = None,
    ):
        super().__init__(client_factory=client_factory, timeout=timeout)
        self._result: list[SecurityWeightDict] = []

    @override
    @moex_circuit_breaker  # type: ignore[misc]
    async def get_index_content(self) -> list[SecurityWeightDict]:
        try:
            async with self:
                await self._collect_weights()
        except Exception:
            logger.exception(
                'Unexpected error while collecting IMOEX index weights',
            )
            raise

        return self._result

    async def _collect_weights(self) -> None:
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
                    'ticker': typing.cast(str, security['ticker']),
                    'weight': typing.cast(float, security['weight']),
                },
            )
