from django.contrib.auth import get_user_model
from django.test import TestCase

import exchange.models
import portfolio.models
import users.models


class PortfolioModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stock1: exchange.models.Security = (
            exchange.models.Security.objects.create(ticker='T')
        )
        cls.stock2: exchange.models.Security = (
            exchange.models.Security.objects.create(ticker='SBER')
        )

        cls.user: users.models.ItableUser = (
            get_user_model().objects.create_user(
                username='testuser',
                password='password',
            )
        )
        cls.portfolio: portfolio.models.Portfolio = (
            portfolio.models.Portfolio.objects.create(
                name='Test Portfolio',
                user=cls.user,
            )
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

        last_portfolio_item: portfolio.models.PortfolioItem = (
            await self.portfolio.items.select_related('security').alast()
        )
        self.assertEqual(last_portfolio_item.quantity, 5)
        self.assertEqual(last_portfolio_item.security.ticker, 'SBER')
