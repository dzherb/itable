import asyncio

import aiohttp
import aiomoex

from exchange.exchange import IndexAPIProtocol, SecurityDict


class _MOEXBaseApi:
    BASE_URL = 'https://iss.moex.com/iss'

    def __init__(self):
        self._session = None

    def _get_iss_client(
        self,
        request_url: str,
        arguments: dict | None = None,
    ) -> aiomoex.ISSClient:
        return aiomoex.ISSClient(
            self._session,
            self.BASE_URL + request_url,
            arguments,
        )


class IMOEXApi(_MOEXBaseApi, IndexAPIProtocol):
    def __init__(self):
        super().__init__()
        self._result: dict[str, SecurityDict] = {}

    async def get_index_content(self) -> list[SecurityDict]:
        async with aiohttp.ClientSession() as session:
            self._session = session
            await asyncio.gather(
                self._collect_weights(),
                self._collect_prices(),
            )
            await self._collect_dividends()

        return [
            security
            for security in self._result.values()
            if security.get('ticker')
        ]

    async def _collect_weights(self):
        request_url = (
            '/statistics/engines/stock/markets/index/analytics/IMOEX.json'
        )
        arguments = {'limit': 100}
        client = self._get_iss_client(request_url, arguments)
        data = await client.get()
        for security in data['analytics']:
            secid = security['secids']

            self._result[secid] = self._result.get(secid, {}) | {
                'ticker': security['ticker'],
                'short_name': security['shortnames'],
                'weight': security['weight'],
            }

    async def _collect_prices(self):
        request_url = (
            '/engines/stock/markets/shares/boards/TQBR/securities.json'
        )
        client = self._get_iss_client(request_url)
        data = await client.get()

        for security in data['securities']:
            secid = security['SECID']

            self._result[secid] = self._result.get(secid, {}) | {
                'price': security['PREVPRICE'],
                'lot_size': security['LOTSIZE'],
            }

    async def _collect_dividends(self):
        tasks = []
        for ticker in self._result.keys():
            if not self._result[ticker].get('ticker'):
                continue

            request_url = f'/securities/{ticker}/dividends.json'
            client = self._get_iss_client(request_url)
            tasks.append(client.get())

        for task in asyncio.as_completed(tasks):
            data = await task
            dividends = data['dividends']
            if not dividends:
                continue

            last_dividend = dividends[-1]
            secid = last_dividend['secid']
            self._result[secid]['last_dividend_value'] = last_dividend['value']
