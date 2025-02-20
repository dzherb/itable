from http import HTTPStatus

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse

User = get_user_model()


class AuthTestsMixin:
    def setUp(self):
        self.client = AsyncClient()

    async def _create_user(self):
        return await sync_to_async(User.objects.create_user)(
            username='test_user',
            password='password',
        )


class LoginCase(AuthTestsMixin, TestCase):
    async def test_login_with_correct_credentials(self):
        user = await self._create_user()
        response = await self.client.post(
            reverse('api:login'),
            data={'username': 'test_user', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        session = await self.client.asession()
        self.assertEqual(int(await session.aget('_auth_user_id')), user.id)

    async def test_login_with_wrong_credentials(self):
        response = await self.client.post(
            reverse('api:login'),
            data={'username': 'test_user', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_login_with_wrong_schema(self):
        response = await self.client.post(
            reverse('api:login'),
            data={'email': 'test@test.com', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class LogoutTestCase(AuthTestsMixin, TestCase):
    async def test_authenticated_user_can_logout(self):
        user = await self._create_user()

        await self.client.aforce_login(user)
        response = await self.client.post(reverse('api:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        session = await self.client.asession()
        self.assertEqual(await session.aget('_auth_user_id'), None)

    async def test_anonymous_user_can_logout(self):
        response = await self.client.post(reverse('api:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
