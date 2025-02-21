import dataclasses
from http import HTTPStatus
import json
from typing import override

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import AsyncRequestFactory, TestCase

from api.helpers import aget_object_or_404_json
from api.permissions.permission_protocol import Permission
from api.views.api_view import api_view, Checker

User = get_user_model()


class UsernameLenIs10Permission(Permission):
    @override
    async def has_permission(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> bool:
        return (
            request.user.is_authenticated and len(request.user.username) == 10
        )


class RequestHasAcceptCharsetHeaderChecker(Checker):
    @override
    async def check(self, request: HttpRequest, *args, **kwargs) -> bool:
        return 'Accept-Charset' in request.headers

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': 'Expected Accept-Charset header'},
            status=HTTPStatus.BAD_REQUEST,
        )


class APIViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()
        cls.user = User.objects.create_user(username='user', password='123')

    async def test_api_view_can_be_applied_without_arguments(self):
        @api_view
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get(path='/hello_world')
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(content['message'], 'hello world')

    async def test_api_view_can_be_applied_with_arguments(self):
        @api_view(methods=['GET'])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get(path='/hello_world')
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(content['message'], 'hello world')

    async def test_api_view_checks_allowed_methods(self):
        @api_view(methods=['POST'])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get(path='/hello_world')
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(content['error'], 'Method not allowed')

    async def test_api_view_checks_permissions_and_not_allows(self):
        @api_view(permissions=[UsernameLenIs10Permission()])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get(path='/hello_world')
        request.user = self.user
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(content['error'], 'Permission denied')

    async def test_api_view_checks_permissions_and_allows(self):
        class UsernameLenIs4Permission(Permission):
            @override
            async def has_permission(
                self,
                request: HttpRequest,
                *args,
                **kwargs,
            ) -> bool:
                return (
                    request.user.is_authenticated
                    and len(request.user.username) == 4
                )

        @api_view(permissions=[UsernameLenIs4Permission()])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get('/hello_world')
        request.user = self.user
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(content['message'], 'hello world')

    async def test_can_use_custom_checker(self):
        @api_view(checkers=[RequestHasAcceptCharsetHeaderChecker()])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        valid_request = self.factory.get(
            path='/hello_world',
            headers={'Accept-Charset': 'utf-8'},
        )
        response = await hello_world(valid_request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(content['message'], 'hello world')

        not_valid_request = self.factory.get('/hello_world')
        response = await hello_world(not_valid_request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(content['error'], 'Expected Accept-Charset header')

    async def test_not_found_exception_is_intercepted(self):
        @api_view
        async def user_handler(request):
            user = await aget_object_or_404_json(User, pk=42)
            return JsonResponse({'user_id': user.id})

        request = self.factory.get(path='/user_handler')
        response = await user_handler(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(content['error'], 'not found')


@dataclasses.dataclass
class UserSchema:
    username: str
    password: str
    age: int | None


class APIViewSchemaTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()

        @api_view(methods=['POST'], request_schema=UserSchema)
        async def echo(request):
            user = request.populated_schema
            return JsonResponse(dataclasses.asdict(user))

        cls.echo_handler = echo

    async def test_request_body_populates_the_schema(self):
        valid_request_data = [
            {'username': 'test_user', 'password': 'password'},
            {'username': 'test_user', 'password': 'password', 'age': 20},
        ]

        for request_data in valid_request_data:
            with self.subTest(request_data=request_data):
                request = self.factory.post(
                    path='/echo',
                    data=request_data,
                    content_type='application/json',
                )
                response = await self.echo_handler(request)
                content = json.loads(response.content)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                for key, value in request_data.items():
                    self.assertEqual(content[key], value)

    async def test_api_view_returns_error_on_invalid_data(self):
        wrong_request_data = [
            {'username': 'test_user'},
            {'username': 'test_user', 'password': 123456},
            {'username1': 'test_user', 'password': '123456'},
        ]

        for request_data in wrong_request_data:
            with self.subTest(request_data=request_data):
                request = self.factory.post(
                    path='/echo',
                    data=request_data,
                    content_type='application/json',
                )
                response = await self.echo_handler(request)
                content = json.loads(response.content)

                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertIn('error', content)

    async def test_api_view_handles_invalid_json(self):
        request = self.factory.generic(
            method='POST',
            path='/echo',
            data='{"id": 15',
            content_type='application/json',
        )
        response = await self.echo_handler(request)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('error', content)


@dataclasses.dataclass
class UserSchemaWithValidators:
    username: str
    password: str
    age: int | None

    def validate(self):
        if self.username.lower() in self.password.lower():
            raise ValueError('password contains username')

    def validate_age(self):
        if self.age is not None and self.age < 1:
            raise ValueError('age is too small')

    def validate_password(self):
        if len(self.password) < 8:
            raise ValueError('password is too short')

        if self.password.isnumeric():
            raise ValueError('password should include letters')


class APIViewSchemaValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()

        @api_view(methods=['POST'], request_schema=UserSchemaWithValidators)
        async def handler(request):
            return JsonResponse({}, status=HTTPStatus.OK)

        cls.handler = handler

    async def test_api_view_schema_field_validation_failure(self):
        cases = [
            (
                {'username': 'test', 'password': 'strong1Pass', 'age': 0},
                'age is too small',
            ),
            (
                {'username': 'test', 'password': 'pass', 'age': 18},
                'password is too short',
            ),
            (
                {'username': 'test', 'password': '12345678', 'age': 18},
                'password should include letters',
            ),
        ]

        for case in cases:
            with self.subTest(case=case):
                request_data, expected_error = case

                request = self.factory.post(
                    path='/handler',
                    data=request_data,
                    content_type='application/json',
                )
                response = await self.handler(request)
                content = json.loads(response.content)
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertEqual(content['error'], expected_error)

    async def test_api_view_schema_field_validation_success(self):
        request_data = {
            'username': 'test',
            'password': 'strong1Pass',
            'age': 18,
        }
        request = self.factory.post(
            path='/handler',
            data=request_data,
            content_type='application/json',
        )
        response = await self.handler(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)


class APIViewAuthenticationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()

        @api_view(methods=['GET'], login_required=True)
        async def handler(request):
            return JsonResponse({}, status=HTTPStatus.OK)

        cls.handler = handler
        cls.user = User.objects.create_user(
            username='test',
            password='password',
        )

    def _attach_user_to_mocked_request(self, request, user):
        async def auser():
            return user

        request.auser = auser

    async def test_authenticated_user_has_access(self):
        request = self.factory.get(path='/handler')
        self._attach_user_to_mocked_request(request, self.user)

        response = await self.handler(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_anonymous_user_has_no_access(self):
        request = self.factory.get(path='/handler')
        self._attach_user_to_mocked_request(request, AnonymousUser())

        response = await self.handler(request)
        error = json.loads(response.content)['error']

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(error, 'authentication required')
