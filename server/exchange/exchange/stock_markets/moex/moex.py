import asyncio
from collections.abc import Iterable
import logging
from types import TracebackType
import typing
from typing import override

import aiohttp
import aiohttp.web_exceptions
import aiomoex

from exchange.exchange.stock_markets.moex.iss_client import (
    ISSClient,
    ISSClientFactory,
    ISSClientFactoryImpl,
)
from exchange.exchange.stock_markets.stock_market_protocol import (
    PartialSecurityDict,
    SecurityDict,
    StockMarketProtocol,
)
from utils.cache import alru_method_shared_cache
from utils.circuit_breaker import ResettableCircuitBreaker

logger = logging.getLogger('exchange.stock_markets')


class MOEXError(Exception):
    pass


class MOEXConnectionError(MOEXError):
    pass


class MOEXServerError(MOEXError):
    pass


class MOEXCircuitBreaker(ResettableCircuitBreaker):
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 30
    EXPECTED_EXCEPTION = MOEXError


moex_circuit_breaker: typing.Final[ResettableCircuitBreaker] = (
    MOEXCircuitBreaker()
)

DEFAULT_TIMEOUT: typing.Final = aiohttp.ClientTimeout(total=10)


class BaseMOEX:
    def __init__(
        self,
        *,
        client_factory: ISSClientFactory | None = None,
        timeout: aiohttp.ClientTimeout | int | None = None,
    ):
        self._client_factory: ISSClientFactory = (
            client_factory or ISSClientFactoryImpl()
        )
        self._session: aiohttp.ClientSession
        self._timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            raise_for_status=True,
            timeout=self._timeout,
        )
        await self._session.__aenter__()
        return

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        await self._session.__aexit__(exc_type, exc_val, exc_tb)

        if exc_val:
            if isinstance(exc_val, aiohttp.ClientError):
                raise MOEXConnectionError from exc_val
            if isinstance(exc_val, aiohttp.web_exceptions.HTTPServerError):
                raise MOEXServerError from exc_val

            return False

        return None


class MOEX(BaseMOEX, StockMarketProtocol):
    def __init__(
        self,
        *,
        client_factory: ISSClientFactory | None = None,
        timeout: aiohttp.ClientTimeout | int | None = None,
    ):
        super().__init__(client_factory=client_factory, timeout=timeout)

        self._tickers: Iterable[str]
        self._result: dict[str, SecurityDict] = {}

    @override
    @moex_circuit_breaker
    async def get_securities(
        self,
        tickers: Iterable[str],
    ) -> list[SecurityDict]:
        self._tickers = tuple(tickers)
        try:
            async with self:
                return await self._get_securities()
        except Exception:
            logger.error(
                'Unexpected error while collecting securities from MOEX',
                exc_info=True,
            )
            raise

    async def _get_securities(self) -> list[SecurityDict]:
        await asyncio.gather(
            self._collect_securities(),
            self._collect_dividends(),
        )
        return list(self._result.values())

    async def _collect_securities(self):
        resource = '/engines/stock/markets/shares/boards/TQBR/securities.json'
        client = self._get_client(
            resource=resource,
            arguments={'securities': ','.join(self._tickers)},
        )
        data = await client.get()

        for security in data['securities']:
            ticker = typing.cast(str, security['SECID'])

            self._add_to_results(
                ticker,
                {
                    'ticker': ticker,
                    'short_name': typing.cast(str, security['SHORTNAME']),
                    'price': typing.cast(float, security['PREVPRICE']),
                    'lot_size': typing.cast(int, security['LOTSIZE']),
                },
            )

    async def _collect_dividends(self):
        tasks = []
        for ticker in self._tickers:
            tasks.append(self._get_dividends_for_ticker(ticker))

        for task in asyncio.as_completed(tasks):
            dividends = await task
            if not dividends:
                continue

            last_dividend = dividends[-1]
            ticker = last_dividend['secid']

            self._add_to_results(
                ticker,
                {
                    'last_dividend_value': last_dividend['value'],
                },
            )

    @alru_method_shared_cache(ttl=20 * 60)
    async def _get_dividends_for_ticker(
        self,
        ticker: str,
    ) -> aiomoex.client.Table:
        resource = f'/securities/{ticker}/dividends.json'
        client = self._get_client(resource)
        return (await client.get())['dividends']

    def _get_client(
        self,
        resource: str,
        arguments: aiomoex.client.WebQuery | None = None,
    ) -> ISSClient:
        assert self._session is not None
        return self._client_factory.get_client(
            self._session,
            resource,
            arguments,
        )

    def _add_to_results(
        self,
        ticker: str,
        partial_security: PartialSecurityDict,
    ):
        default_security = SecurityDict(
            short_name='',
            ticker=ticker,
            price=0,
            lot_size=1,
        )
        self._result[ticker] = (
            self._result.get(ticker, default_security) | partial_security
        )
