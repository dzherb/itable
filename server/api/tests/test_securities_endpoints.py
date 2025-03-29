from http import HTTPStatus
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse

from api.tests.helpers import generate_auth_header
from exchange.services.stock_markets import MOEX
from exchange.tests.test_moex_integration import MockISSClientFactory

User = get_user_model()


class SecurityListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='testuser',
            password='123456',
        )

    def setUp(self):
        self.client = AsyncClient()
        self.credentials = generate_auth_header(self.user)

    @mock.patch('api.views.securities.securities.MOEX')
    async def test_security_list_successful_request(self, moex_mock):
        moex_mock.return_value = MOEX(client_factory=MockISSClientFactory())
        response = await self.client.get(
            reverse('api:securities'),
            query_params={'tickers': ['LKOH', 'GAZP']},
            headers=self.credentials,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json()['securities']), 2)

    async def test_security_list_unauthorized_request(self):
        response = await self.client.get(
            reverse('api:securities'),
            query_params={'tickers': ['LKOH', 'GAZP']},
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_security_list_invalid_params_request(self):
        response = await self.client.get(
            reverse('api:securities'),
            query_params={'test': ['LKOH', 'GAZP']},
            headers=self.credentials,
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
