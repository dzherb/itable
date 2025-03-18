from http import HTTPStatus
import json

from asgiref.sync import sync_to_async
from django.contrib.auth import aauthenticate, get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse

from api.tests.helpers import agenerate_auth_header
from users.models import ItableUser

User = get_user_model()


class AuthTestsMixin:
    def setUp(self):
        self.client = AsyncClient()

    async def _create_user(self) -> ItableUser:
        user: ItableUser = await sync_to_async(User.objects.create_user)(
            email='test_user',
            password='password',
        )
        await user.generate_new_tokens()
        return user


class LoginCase(AuthTestsMixin, TestCase):
    async def test_login_with_correct_credentials(self):
        user = await self._create_user()
        response = await self.client.post(
            reverse('api:login'),
            data={'email': 'test_user', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)
        user_from_token = await aauthenticate(
            access_token=content['access_token'],
        )
        self.assertEqual(user_from_token, user)

    async def test_login_with_wrong_credentials(self):
        response = await self.client.post(
            reverse('api:login'),
            data={'email': 'test_user', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        content = json.loads(response.content)
        self.assertEqual(content, {'error': 'invalid credentials'})

    async def test_login_with_wrong_schema(self):
        response = await self.client.post(
            reverse('api:login'),
            data={'test': 'test', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        content = json.loads(response.content)
        self.assertEqual(content, {'error': 'missing value for field "email"'})


class LogoutTestCase(AuthTestsMixin, TestCase):
    async def test_authenticated_user_can_logout(self):
        user = await self._create_user()
        old_refresh_token = user.refresh_token

        response = await self.client.post(
            reverse('api:logout'),
            headers=await agenerate_auth_header(user),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        await user.arefresh_from_db()
        self.assertFalse(user.can_refresh_tokens(old_refresh_token))

    async def test_anonymous_user_can_logout(self):
        response = await self.client.post(reverse('api:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class FullAuthScreenplayTestCase(AuthTestsMixin, TestCase):
    async def test_user_can_login_and_use_token_for_authentication(self):
        await self._create_user()
        response = await self.client.post(
            reverse('api:login'),
            data={'email': 'test_user', 'password': 'password'},
            content_type='application/json',
        )
        content = json.loads(response.content)
        access_token = content['access_token']

        response = await self.client.get(
            reverse('api:portfolios'),
            headers={'Authorization': f'Token {access_token}'},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
