from http import HTTPStatus
import json
from unittest import mock

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import aauthenticate, get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse
from django.utils import timezone

from api.tests.helpers import agenerate_auth_header
from apps.users.authentication.jwt import TokenPair
from apps.users.models import ItableUser

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


class AuthScreenplaysTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user: ItableUser = User.objects.create_user(
            email='test_user',
            password='password',
            is_staff=True,
        )

    def setUp(self):
        self.client = AsyncClient()

    async def _login(self) -> TokenPair:
        response = await self.client.post(
            reverse('api:login'),
            data={'email': 'test_user', 'password': 'password'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)
        return TokenPair(content['access_token'], content['refresh_token'])

    async def test_user_can_use_access_token_for_authentication(self):
        token_pair = await self._login()

        response = await self.client.get(
            reverse('api:portfolios'),
            headers={'Authorization': f'Bearer {token_pair.access_token}'},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_user_cant_use_artificial_access_token(self):
        response = await self.client.get(
            reverse('api:portfolios'),
            headers={'Authorization': 'Bearer this_is_definitely_not_a_token'},
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_access_token_expires(self):
        token_pair = await self._login()
        with mock.patch(
            'apps.users.authentication.jwt.timezone',
        ) as mock_timezone:
            mock_timezone.now.return_value = (
                timezone.now() + settings.ACCESS_TOKEN_TIME_TO_LIVE
            )
            response = await self.client.get(
                reverse('api:portfolios'),
                headers={'Authorization': f'Bearer {token_pair.access_token}'},
            )
            self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_user_can_refresh_tokens(self):
        token_pair = await self._login()

        response = await self.client.post(
            reverse('api:refresh'),
            data={'refresh_token': token_pair.refresh_token},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = json.loads(response.content)
        new_access_token = content['access_token']

        response = await self.client.get(
            reverse('api:portfolios'),
            headers={'Authorization': f'Bearer {new_access_token}'},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_can_refresh_after_access_token_expiration(self):
        token_pair = await self._login()
        with mock.patch(
            'apps.users.authentication.jwt.timezone',
        ) as mock_timezone:
            mock_timezone.now.return_value = (
                timezone.now() + settings.ACCESS_TOKEN_TIME_TO_LIVE
            )

            response = await self.client.post(
                reverse('api:refresh'),
                data={'refresh_token': token_pair.refresh_token},
                content_type='application/json',
            )

        content = json.loads(response.content)
        new_access_token = content['access_token']

        response = await self.client.get(
            reverse('api:portfolios'),
            headers={'Authorization': f'Bearer {new_access_token}'},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_cant_refresh_after_refresh_token_expiration(self):
        token_pair = await self._login()
        with mock.patch(
            'apps.users.authentication.jwt.timezone',
        ) as mock_timezone:
            mock_timezone.now.return_value = (
                timezone.now() + settings.REFRESH_TOKEN_TIME_TO_LIVE
            )

            response = await self.client.post(
                reverse('api:refresh'),
                data={'refresh_token': token_pair.refresh_token},
                content_type='application/json',
            )
            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    async def test_sessions_based_authorization_continues_to_work(self):
        token_pair = await self._login()
        await self.client.aforce_login(self.user)

        response = await self.client.get(
            reverse('api:portfolios'),
            headers={'Authorization': f'Bearer {token_pair.access_token}'},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = await self.client.get(
            reverse('admin:index'),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_api_view_doesnt_accept_sessions_based_authorization(self):
        await self.client.aforce_login(self.user)

        response = await self.client.get(
            reverse('api:portfolios'),
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
