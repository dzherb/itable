from http import HTTPStatus
import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.test import AsyncClient, TestCase
from django.urls import reverse
from parameterized import parameterized

from exchange.exchange.stock_markets import MOEX
from exchange.models import Security
from exchange.tests.test_moex_integration import MockISSClientFactory
from portfolio.models import Portfolio, PortfolioItem
from utils.db_helpers import AsyncAtomic

User = get_user_model()


class PortfolioEndpointTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.portfolio_owner = User.objects.create_user(
            email='owner',
            password='password',
        )
        cls.not_portfolio_owner = User.objects.create_user(
            email='just_user',
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


class PortfolioListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create_user(
            email='user1',
            password='password',
        )
        cls.second_user = User.objects.create_user(
            email='user2',
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

    async def test_user_can_create_portfolio(self):
        await self.client.aforce_login(self.first_user)
        response = await self.client.post(
            self.endpoint_path,
            data={'name': 'my super portfolio'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        portfolio = json.loads(response.content)
        created_portfolio: Portfolio = await Portfolio.objects.alast()

        self.assertEqual(portfolio['name'], 'my super portfolio')
        self.assertEqual(portfolio['id'], created_portfolio.id)

    async def test_anonymous_user_cant_create_portfolio(self):
        response = await self.client.post(
            self.endpoint_path,
            data={'name': 'my super portfolio'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(await Portfolio.objects.acount(), 3)

    async def test_user_cant_create_portfolio_with_empty_name(self):
        await self.client.aforce_login(self.first_user)
        response = await self.client.post(
            self.endpoint_path,
            data={'name': ''},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        error = json.loads(response.content)['error']
        self.assertEqual(error, 'name cannot be empty')


class PortfolioSecurityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create_user(
            email='user1',
            password='password',
        )
        cls.second_user = User.objects.create_user(
            email='user2',
            password='password',
        )
        cls.first_user_portfolio = Portfolio.objects.create(
            name='user1 portfolio',
            owner=cls.first_user,
        )
        cls.security1 = Security.objects.create(ticker='SBER')
        cls.security2 = Security.objects.create(ticker='T')

        cls.endpoint_path = reverse(
            'api:portfolio_securities',
            args=(cls.first_user_portfolio.id,),
        )

    def setUp(self):
        self.client = AsyncClient()

    async def test_user_can_add_security_to_portfolio(self):
        await self.client.aforce_login(self.first_user)
        response = await self.client.post(
            self.endpoint_path,
            data={'ticker': 'SBER', 'quantity': 1},
            content_type='application/json',
        )
        portfolio_security = json.loads(response.content)
        portfolio_item: PortfolioItem = (
            await PortfolioItem.objects.select_related('portfolio').alast()
        )

        self.assertEqual(portfolio_security['ticker'], 'SBER')
        self.assertEqual(portfolio_security['quantity'], 1)
        self.assertEqual(portfolio_item.portfolio, self.first_user_portfolio)

    async def test_anonymous_user_cant_add_security_to_portfolio(self):
        response = await self.client.post(
            self.endpoint_path,
            data={'ticker': 'SBER', 'quantity': 1},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_user_cant_add_same_security_twice(self):
        await self.client.aforce_login(self.first_user)
        response = await self.client.post(
            self.endpoint_path,
            data={'ticker': 'SBER', 'quantity': 1},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        async with AsyncAtomic():
            response = await self.client.post(
                self.endpoint_path,
                data={'ticker': 'SBER', 'quantity': 5},
                content_type='application/json',
            )

        error = json.loads(response.content)['error']

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(error, 'security already exists')
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            1,
        )

    async def test_user_cant_add_security_to_deleted_portfolio(self):
        await self.client.aforce_login(self.first_user)
        self.first_user_portfolio.is_active = False
        await self.first_user_portfolio.asave(update_fields=['is_active'])

        response = await self.client.post(
            self.endpoint_path,
            data={'ticker': 'SBER', 'quantity': 1},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        error = json.loads(response.content)['error']
        self.assertEqual(error, 'portfolio not found')

    @mock.patch('exchange.models.security.MOEX')
    async def test_user_cant_add_nonexistent_security(self, mock_moex):
        # Use mock because if there is no such security in db,
        # we attempt to create it from MOEX
        mock_moex.return_value = MOEX(client_factory=MockISSClientFactory())

        await self.client.aforce_login(self.first_user)

        response = await self.client.post(
            self.endpoint_path,
            data={'ticker': 'TEST', 'quantity': 23},
            content_type='application/json',
        )
        error = json.loads(response.content)['error']

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(error, 'security not found')
        self.assertFalse(await self.first_user_portfolio.securities.aexists())

    async def test_user_can_update_portfolio_security_quantity(self):
        await self.client.aforce_login(self.first_user)
        url = await self._add_security_to_portfolio_and_get_its_url()
        response = await self.client.patch(
            url,
            {'ticker': 'SBER', 'quantity': 5},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        portfolio_item: PortfolioItem = (
            await self.first_user_portfolio.items.alast()
        )
        self.assertEqual(portfolio_item.quantity, 5)

    @parameterized.expand(
        [
            ('SBER', {'quantity': 0}, HTTPStatus.BAD_REQUEST),
            ('SBER', {'quantity': -2}, HTTPStatus.BAD_REQUEST),
            ('SBER', {'quantity': '1'}, HTTPStatus.BAD_REQUEST),
            ('SBER', {'quantity': None}, HTTPStatus.BAD_REQUEST),
            ('SBER', {}, HTTPStatus.BAD_REQUEST),
            ('T', {'quantity': 4}, HTTPStatus.NOT_FOUND),
        ],
    )
    async def test_user_cant_update_portfolio_security_quantity(
        self,
        ticker,
        request_data,
        expected_status,
    ):
        await self.client.aforce_login(self.first_user)
        await self._add_security_to_portfolio_and_get_its_url()

        url = reverse(
            'api:portfolio_security',
            kwargs={
                'portfolio_id': self.first_user_portfolio.id,
                'security_ticker': ticker,
            },
        )
        response = await self.client.patch(
            url,
            data=request_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, expected_status)

    async def test_user_can_delete_portfolio_security(self):
        await self.client.aforce_login(self.first_user)
        url = await self._add_security_to_portfolio_and_get_its_url()
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            1,
        )

        response = await self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            0,
        )

    async def test_user_cant_delete_same_portfolio_security_twice(self):
        await self.client.aforce_login(self.first_user)
        url = await self._add_security_to_portfolio_and_get_its_url()

        response = await self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            0,
        )

        response = await self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        error = json.loads(response.content)['error']
        self.assertEqual(error, 'portfolio security not found')
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            0,
        )

    async def test_user_cant_delete_deleted_portfolio_security(self):
        await self.client.aforce_login(self.first_user)
        url = await self._add_security_to_portfolio_and_get_its_url()
        self.first_user_portfolio.is_active = False
        await self.first_user_portfolio.asave(update_fields=['is_active'])
        response = await self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        error = json.loads(response.content)['error']
        self.assertEqual(error, 'portfolio not found')

    async def test_user_cant_delete_not_theirs_portfolio_security(self):
        await self.client.aforce_login(self.first_user)
        url = await self._add_security_to_portfolio_and_get_its_url()

        await self.client.aforce_login(self.second_user)
        response = await self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            1,
        )
        error = json.loads(response.content)['error']
        self.assertEqual(error, 'portfolio not found')

    async def test_anonymous_user_cant_delete_portfolio_security(self):
        await self.client.aforce_login(self.first_user)
        url = await self._add_security_to_portfolio_and_get_its_url()
        await self.client.alogout()
        response = await self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(
            await self.first_user_portfolio.securities.acount(),
            1,
        )

    async def _add_security_to_portfolio_and_get_its_url(self) -> str:
        await self.client.post(
            self.endpoint_path,
            data={'ticker': 'SBER', 'quantity': 13},
            content_type='application/json',
        )

        return reverse(
            'api:portfolio_security',
            kwargs={
                'portfolio_id': self.first_user_portfolio.id,
                'security_ticker': 'SBER',
            },
        )
