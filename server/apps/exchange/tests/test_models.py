from unittest import mock

from django.test import TestCase

from apps.exchange.models import Security
from apps.exchange.tests.test_moex_integration import MockISSClientFactory
from services.exchange.stock_markets import MOEX


class SecurityTestCase(TestCase):
    @mock.patch('apps.exchange.models.security.MOEX')
    async def test_can_create_from_moex_if_exists(self, mock_moex):
        mock_moex.return_value = MOEX(client_factory=MockISSClientFactory())
        self.assertFalse(await Security.objects.aexists())

        security = await Security.create_from_moex_if_exists(ticker='GMKN')
        self.assertEqual(security.ticker, 'GMKN')

        self.assertTrue(await Security.objects.aexists())

    @mock.patch('apps.exchange.models.security.MOEX')
    async def test_cant_create_from_moex_if_doesnt_exist(self, mock_moex):
        mock_moex.return_value = MOEX(client_factory=MockISSClientFactory())
        self.assertFalse(await Security.objects.aexists())

        security = await Security.create_from_moex_if_exists(ticker='UNKNOWN')
        self.assertIsNone(security)

        self.assertFalse(await Security.objects.aexists())

    @mock.patch('apps.exchange.models.security.MOEX')
    async def test_get_or_try_to_create_from_moex(self, mock_moex):
        mock_moex.return_value = MOEX(client_factory=MockISSClientFactory())
        self.assertFalse(await Security.objects.aexists())
        await Security.objects.acreate(ticker='TEST')

        security = await Security.get_or_try_to_create_from_moex(ticker='TEST')
        self.assertEqual(security.ticker, 'TEST')
        self.assertEqual(await Security.objects.acount(), 1)

    @mock.patch('apps.exchange.models.security.MOEX')
    async def test_get_or_try_to_create_from_moex_error(self, mock_moex):
        mock_moex.return_value = MOEX(client_factory=MockISSClientFactory())
        self.assertFalse(await Security.objects.aexists())

        with self.assertRaises(Security.DoesNotExist):
            await Security.get_or_try_to_create_from_moex(ticker='TEST')

        self.assertFalse(await Security.objects.aexists())
