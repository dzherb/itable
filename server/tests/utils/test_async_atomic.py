import asyncio

from django.test import TestCase

from apps.exchange.models import Security
from utils.db_helpers import aatomic, AsyncAtomic


class AsyncAtomicTestCase(TestCase):
    async def test_transaction_commits(self):
        async with AsyncAtomic():
            await Security.objects.acreate(ticker='SBER')

        last_security = await Security.objects.alast()
        self.assertEqual(last_security.ticker, 'SBER')

    async def test_transaction_rollbacks(self):
        try:
            async with AsyncAtomic():
                await self._create_securities_and_raise_exception()
        except Exception:
            pass

        self.assertFalse(await Security.objects.aexists())

    async def test_decorator_usage_is_equivalent_to_context_manager(self):
        try:
            await aatomic(self._create_securities_and_raise_exception)()
        except Exception:
            pass

        self.assertFalse(await Security.objects.aexists())

    async def test_side_tasks_dont_participate_in_transaction(self):
        tickers = [str(i) for i in range(100)]
        side_tasks = [
            Security.objects.acreate(ticker=ticker) for ticker in tickers
        ]

        try:
            async with AsyncAtomic():
                await self._create_securities_and_raise_exception()
        except Exception:
            pass

        await asyncio.gather(*side_tasks)
        async for security in Security.objects.all():
            self.assertIn(security.ticker, tickers)

    async def _create_securities_and_raise_exception(self):
        tasks = [
            Security.objects.acreate(ticker='SBER'),
            Security.objects.acreate(ticker='T'),
            Security.objects.acreate(ticker='YDEX'),
        ]
        await asyncio.gather(*tasks)
        raise Exception
