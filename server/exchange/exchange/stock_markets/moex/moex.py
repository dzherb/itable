import asyncio
from collections.abc import Iterable

import aiohttp
import aiomoex

from exchange.exchange.stock_markets.moex.iss_client import (
    ISSClient,
    ISSClientFactory,
    ISSClientFactoryImpl,
)
from exchange.exchange.stock_markets.stock_market_protocol import (
    SecurityDict,
    StockMarketProtocol,
)
from utils.cache import alru_method_shared_cache


class MOEX(StockMarketProtocol):
    def __init__(self, *, client_factory: ISSClientFactory | None = None):
        self._client_factory: ISSClientFactory = (
            client_factory or ISSClientFactoryImpl()
        )
        self._session: aiohttp.ClientSession | None = None
        self._tickers: set[str] | None = None
        self._result: dict[str, SecurityDict] = {}

    async def get_securities(
        self,
        tickers: Iterable[str],
    ) -> list[SecurityDict]:
        self._tickers = tuple(tickers)

        async with aiohttp.ClientSession() as session:
            self._session = session
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
            ticker = security['SECID']

            self._add_to_results(
                ticker,
                {
                    'ticker': security['SECID'],
                    'short_name': security['SHORTNAME'],
                    'price': security['PREVPRICE'],
                    'lot_size': security['LOTSIZE'],
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
        return self._client_factory.get_client(
            self._session,
            resource,
            arguments,
        )

    def _add_to_results(self, ticker: str, security: dict):
        self._result[ticker] = self._result.get(ticker, {}) | security
