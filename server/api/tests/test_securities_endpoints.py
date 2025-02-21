from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse

User = get_user_model()


class SecurityListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='123456',
        )

    def setUp(self):
        self.client = AsyncClient()

    async def test_security_list_successful_request(self):
        await self.client.aforce_login(self.user)
        response = await self.client.get(
            reverse('api:securities'),
            query_params={'tickers': ['SBER', 'T']},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.json()['securities']), 2)

    async def test_security_list_unauthorized_request(self):
        response = await self.client.get(
            reverse('api:securities'),
            query_params={'tickers': ['SBER', 'T']},
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_security_list_invalid_params_request(self):
        await self.client.aforce_login(self.user)
        response = await self.client.get(
            reverse('api:securities'),
            query_params={'test': ['SBER', 'T']},
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
