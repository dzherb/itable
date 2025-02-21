from http import HTTPStatus
import json

from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.test import AsyncClient, TestCase
from django.urls import reverse

from exchange.models import Security
from portfolio.models import Portfolio

User = get_user_model()


class PortfolioEndpointTestCase(TestCase):
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

        cls.security1 = Security.objects.create(ticker='SBER')
        cls.security2 = Security.objects.create(ticker='T')
        cls.portfolio.securities.add(
            cls.security1,
            through_defaults={'quantity': 2},
        )
        cls.portfolio.securities.add(
            cls.security2,
            through_defaults={'quantity': 5},
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

        expected = json.dumps(
            {
                'id': self.portfolio.id,
                'name': 'Test Portfolio',
                'owner_id': self.portfolio_owner.pk,
                'created_at': self.portfolio.created_at,
                'securities': [
                    {'ticker': 'SBER', 'quantity': 2},
                    {'ticker': 'T', 'quantity': 5},
                ],
            },
            cls=DjangoJSONEncoder,
        )
        self.assertJSONEqual(response.content.decode(), expected)

    async def test_other_user_cant_get_portfolio(self):
        await self.client.aforce_login(self.not_portfolio_owner)
        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    async def test_anonymous_user_cant_get_portfolio(self):
        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_portfolio_owner_can_delete_portfolio(self):
        await self.client.aforce_login(self.portfolio_owner)
        response = await self.client.delete(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    async def test_other_user_cant_delete_portfolio(self):
        await self.client.aforce_login(self.not_portfolio_owner)
        response = await self.client.delete(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    async def test_anonymous_user_cant_delete_portfolio(self):
        response = await self.client.delete(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_portfolio_owner_can_update_portfolio(self):
        await self.client.aforce_login(self.portfolio_owner)
        response = await self.client.patch(
            self.endpoint_path,
            data={'name': 'new name'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        portfolio = json.loads(response.content)
        self.assertEqual(portfolio['name'], 'new name')

        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        portfolio = json.loads(response.content)
        self.assertEqual(portfolio['name'], 'new name')

    async def test_other_user_cant_update_portfolio(self):
        await self.client.aforce_login(self.not_portfolio_owner)
        response = await self.client.patch(
            self.endpoint_path,
            data={'name': 'new name'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    async def test_anonymous_user_cant_update_portfolio(self):
        response = await self.client.patch(
            self.endpoint_path,
            data={'name': 'new name'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_cant_update_deleted_portfolio(self):
        await self.client.aforce_login(self.portfolio_owner)
        await self.client.delete(self.endpoint_path)
        response = await self.client.patch(
            self.endpoint_path,
            data={'name': 'new name'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class PortfolioListEndpointTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create_user(
            username='user1',
            password='password',
        )
        cls.second_user = User.objects.create_user(
            username='user2',
            password='password',
        )

        cls.first_user_portfolio = Portfolio.objects.create(
            owner=cls.first_user,
            name='Test Portfolio',
        )
        cls.first_user_another_portfolio = Portfolio.objects.create(
            owner=cls.first_user,
            name='Test Portfolio2',
        )

        cls.second_user_portfolio = Portfolio.objects.create(
            owner=cls.second_user,
            name='Second User Test Portfolio',
        )

        cls.endpoint_path = reverse('api:portfolios')

    def setUp(self):
        self.client = AsyncClient()

    async def test_user_can_get_only_own_portfolios(self):
        await self.client.aforce_login(self.first_user)
        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        portfolios = json.loads(response.content)['portfolios']

        self.assertEqual(len(portfolios), 2)
        self.assertEqual(portfolios[0]['name'], 'Test Portfolio')
        self.assertEqual(portfolios[1]['name'], 'Test Portfolio2')
        self.assertEqual(
            list(portfolios[0].keys()),
            ['id', 'name', 'owner_id', 'created_at'],
        )

    async def test_anonymous_user_cant_get_portfolios(self):
        response = await self.client.get(self.endpoint_path)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
