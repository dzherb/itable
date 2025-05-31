from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.exchange.models import Security
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.users.models import ItableUser


class PortfolioModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stock1: Security = Security.objects.create(ticker='T')
        cls.stock2: Security = Security.objects.create(ticker='SBER')

        cls.user: ItableUser = get_user_model().objects.create_user(
            email='testuser',
            password='password',
        )
        cls.portfolio: Portfolio = Portfolio.objects.create(
            name='Test Portfolio',
            owner=cls.user,
        )

    async def test_can_add_securities_to_portfolio(self):
        await self.portfolio.securities.aadd(
            self.stock1,
            through_defaults={'quantity': 3},
        )
        await self.portfolio.securities.aadd(
            self.stock2,
            through_defaults={'quantity': 5},
        )
        await self.portfolio.items.acount()
        self.assertEqual(await self.portfolio.items.acount(), 2)

        last_portfolio_item: PortfolioItem = (
            await self.portfolio.items.select_related('security').alast()
        )
        self.assertEqual(last_portfolio_item.quantity, 5)
        self.assertEqual(last_portfolio_item.security.ticker, 'SBER')
