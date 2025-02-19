import aiohttp
import aiomoex
from django.test import TestCase

from exchange.exchange.stock_markets import MOEX
from exchange.exchange.stock_markets.moex.iss_client import (
    ISSClient,
    ISSClientFactory,
)
from exchange.exchange.synchronization.index_providers.imoex import (
    IMOEXProvider,
)


class MockISSClient(ISSClient):
    def __init__(
        self,
        resource: str,
        arguments: aiomoex.client.WebQuery | None = None,
    ):
        self._resource = resource
        self._arguments = arguments

    async def get(self) -> aiomoex.TablesDict:
        if 'IMOEX.json' in self._resource:
            return self._imoex_json()

        if 'dividends.json' in self._resource:
            parts = self._resource.split('/')
            ticker = parts[-2]
            return self._dividends_json(ticker)

        return self._securities_json()

    def _imoex_json(self) -> dict:
        return {
            'analytics': [
                {
                    'indexid': 'IMOEX',
                    'secids': 'GAZP',
                    'shortnames': 'ГАЗПРОМ ао',
                    'ticker': 'GAZP',
                    'tradedate': '2025-02-18',
                    'tradingsession': 3,
                    'weight': 14.55,
                },
                {
                    'indexid': 'IMOEX',
                    'secids': 'GMKN',
                    'shortnames': 'ГМКНорНик',
                    'ticker': 'GMKN',
                    'tradedate': '2025-02-18',
                    'tradingsession': 3,
                    'weight': 3.75,
                },
                {
                    'indexid': 'IMOEX',
                    'secids': 'LKOH',
                    'shortnames': 'ЛУКОЙЛ',
                    'ticker': 'LKOH',
                    'tradedate': '2025-02-18',
                    'tradingsession': 3,
                    'weight': 13.19,
                },
            ],
            'analytics.cursor': [
                {
                    'INDEX': 0,
                    'NEXT_DATE': None,
                    'PAGESIZE': self._arguments['limit'],
                    'PREV_DATE': '2025-02-17',
                    'TOTAL': 3,
                },
            ],
            'analytics.dates': [{'from': '2001-01-03', 'till': '2025-02-18'}],
        }

    def _securities_json(self) -> dict:
        securities = [
            {
                'BOARDID': 'TQBR',
                'CURRENCYID': 'SUR',
                'LATNAME': 'Gazprom',
                'LOTSIZE': 10,
                'PREVPRICE': 180.05,
                'SECID': 'GAZP',
                'SHORTNAME': 'ГАЗПРОМ ао',
            },
            {
                'BOARDID': 'TQBR',
                'CURRENCYID': 'SUR',
                'LATNAME': 'NorNickel GMK',
                'LOTSIZE': 10,
                'PREVPRICE': 138.2,
                'SECID': 'GMKN',
                'SHORTNAME': 'ГМКНорНик',
            },
            {
                'BOARDID': 'TQBR',
                'CURRENCYID': 'SUR',
                'LATNAME': 'LUKOIL',
                'LOTSIZE': 1,
                'PREVPRICE': 7784.5,
                'SECID': 'LKOH',
                'SHORTNAME': 'ЛУКОЙЛ',
            },
            {
                'BOARDID': 'TQBR',
                'CURRENCYID': 'SUR',
                'LATNAME': 'Sberbank',
                'LOTSIZE': 10,
                'PREVPRICE': 319.5,
                'SECID': 'SBER',
                'SHORTNAME': 'Сбербанк',
            },
        ]

        if 'securities' in self._arguments:
            securities = list(
                filter(
                    lambda s: s['SECID'] in self._arguments['securities'],
                    securities,
                ),
            )

        return {'securities': securities}

    def _dividends_json(self, ticker: str) -> dict:
        if ticker in ('LKOH'):
            return {
                'dividends': [
                    {
                        'currencyid': 'RUB',
                        'registryclosedate': '2020-07-17',
                        'secid': ticker,
                        'value': 100.25,
                    },
                    {
                        'currencyid': 'RUB',
                        'registryclosedate': '2021-07-13',
                        'secid': ticker,
                        'value': 123.45,
                    },
                ],
            }

        return {'dividends': []}


class MockISSClientFactory(ISSClientFactory):
    def get_client(
        self,
        session: aiohttp.ClientSession,
        resource: str,
        arguments: aiomoex.client.WebQuery | None = None,
    ) -> ISSClient:
        return MockISSClient(resource, arguments)


class IMOEXProviderTestCase(TestCase):
    async def test_imoex_provider_returns_expected_result(self):
        imoex = IMOEXProvider(client_factory=MockISSClientFactory())
        index_content = await imoex.get_index_content()

        self.assertEqual(len(index_content), 3)

        for security in index_content:
            if security['ticker'] == 'LKOH':
                self.assertEqual(security['weight'], 13.19)
                break


class MOEXTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moex = MOEX(client_factory=MockISSClientFactory())

    async def test_moex_returns_security_for_ticker(self):
        securities = await self.moex.get_securities(['GAZP'])

        self.assertEqual(len(securities), 1)
        self.assertEqual(securities[0]['ticker'], 'GAZP')

    async def test_moex_attaches_last_dividend_if_exists(self):
        securities = await self.moex.get_securities(['GAZP', 'LKOH'])

        self.assertEqual(len(securities), 2)

        for security in securities:
            if security['ticker'] == 'LKOH':
                self.assertEqual(security['last_dividend_value'], 123.45)
            elif security['ticker'] == 'GAZP':
                self.assertNotIn('last_dividend_value', security)

    async def test_moex_ignores_nonexistent_securities(self):
        valid_tickers = ['LKOH', 'GAZP']
        securities = await self.moex.get_securities([*valid_tickers, 'FAKE'])

        self.assertEqual(len(securities), 2)
        for security in securities:
            self.assertTrue(security['ticker'] in valid_tickers)
