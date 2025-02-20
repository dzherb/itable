from http import HTTPStatus
import json

from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse

from portfolio.models import Portfolio

User = get_user_model()


class PortfolioEndpointsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfolio_owner = User.objects.create_user(
            username='owner',
            password='password',
        )
        cls.not_portfolio_owner = User.objects.create_user(
            username='just_user',
            password='password',
        )
        cls.portfolio = Portfolio.objects.create(
            owner=cls.portfolio_owner,
            name='Test Portfolio',
        )

        cls.endpoint_path = reverse(
            'api:portfolio',
            kwargs={'pk': cls.portfolio.pk},
        )

    def setUp(self):
        self.client = AsyncClient()

    async def test_portfolio_owner_can_get_portfolio(self):
        await self.client.aforce_login(self.portfolio_owner)
        response = await self.client.get(self.endpoint_path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        portfolio = json.loads(response.content)

        self.assertEqual(portfolio['name'], 'Test Portfolio')

    async def test_other_user_cant_get_portfolio(self):
        await self.client.aforce_login(self.not_portfolio_owner)
        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    async def test_anonymous_user_cant_get_portfolio(self):
        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
