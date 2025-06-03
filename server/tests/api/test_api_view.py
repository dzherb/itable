# ruff: noqa: PLR2004
import asyncio
import dataclasses
from http import HTTPStatus
import json
from typing import override

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import AsyncRequestFactory, TestCase
from parameterized import param, parameterized

from api.core.api_view import api_view, Checker
from api.permissions.permission_protocol import Permission
from api.request_checkers.schema_checker import SchemaValidationError
from api.utils import aget_object_or_404_json

User = get_user_model()


class EmailLenIs10Permission(Permission):
    @override
    async def has_permission(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> bool:
        return request.user.is_authenticated and len(request.user.email) == 10


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
        cls.user = User.objects.create_user(email='a@a.com', password='123')

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
        @api_view(permissions=[EmailLenIs10Permission()])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get(path='/hello_world')
        request.user = self.user
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(content['error'], 'Permission denied')

    async def test_api_view_checks_permissions_and_allows(self):
        class EmailLenIs7Permission(Permission):
            @override
            async def has_permission(
                self,
                request: HttpRequest,
                *args,
                **kwargs,
            ) -> bool:
                return (
                    request.user.is_authenticated
                    and len(request.user.email) == 7
                )

        @api_view(permissions=[EmailLenIs7Permission()])
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
            user = await aget_object_or_404_json(
                User,
                pk=42,
                object_error_name='user',
            )
            return JsonResponse({'user_id': user.id})

        request = self.factory.get(path='/user_handler')
        response = await user_handler(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(content['error'], 'user not found')


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

    @parameterized.expand(
        [
            ({'username': 'test_user', 'password': 'password'},),
            ({'username': 'test_user', 'password': 'password', 'age': 20},),
        ],
    )
    async def test_request_body_populates_the_schema(self, request_data):
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

    @parameterized.expand(
        [
            ({'username': 'test_user'},),
            ({'username': 'test_user', 'password': 123456},),
            ({'username1': 'test_user', 'password': '123456'},),
        ],
    )
    async def test_api_view_returns_error_on_invalid_data(self, request_data):
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

    def validate(self, request: HttpRequest):
        if self.username.lower() in self.password.lower():
            raise ValueError('password contains username')

    def validate_age(self):
        if self.age < 1:
            raise ValueError('age is too small')

    def validate_password(self):
        if len(self.password) < 8:
            raise ValueError('password is too short')

        if self.password.isnumeric():
            raise ValueError('password should include letters')


@dataclasses.dataclass
class UserSchemaWithMoreComplexValidators:
    username: str
    password: str

    async def validate(self, request: HttpRequest):
        if request.path != '/test_path/':
            raise ValueError('path is not "/test_path/"')

    async def validate_username(self):
        await asyncio.sleep(0)
        if len(self.username) < 3:
            raise ValueError('username is too short')

    def validate_password(self):
        if self.password != 'strong':
            raise SchemaValidationError(
                message='password is invalid',
                response_status=HTTPStatus.UNAUTHORIZED,
            )


class APIViewSchemaValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()

        @api_view(methods=['POST'], request_schema=UserSchemaWithValidators)
        async def handler(request):
            return JsonResponse({}, status=HTTPStatus.OK)

        @api_view(
            methods=['POST'],
            request_schema=UserSchemaWithMoreComplexValidators,
        )
        async def handler_with_complex_schema(request):
            return JsonResponse({}, status=HTTPStatus.OK)

        cls.handler = handler
        cls.handler_with_complex_schema = handler_with_complex_schema

    @parameterized.expand(
        [
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
            (
                {'username': 'test', 'password': '1234test5678', 'age': 18},
                'password contains username',
            ),
        ],
    )
    async def test_api_view_schema_field_validation_failure(
        self,
        request_data,
        expected_error,
    ):
        request = self.factory.post(
            path='/handler',
            data=request_data,
            content_type='application/json',
        )
        response = await self.handler(request)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(content['error'], expected_error)

    @parameterized.expand(
        [
            (
                {
                    'username': 'test',
                    'password': 'strong1Pass',
                    'age': 18,
                },
            ),
            (
                # If a field is Optional, and its value is absent (or None)
                # then we expect to skip its validation
                {
                    'username': 'test',
                    'password': 'strong1Pass',
                },
            ),
            (
                {
                    'username': 'test',
                    'password': 'strong1Pass',
                    'age': None,
                },
            ),
        ],
    )
    async def test_api_view_schema_field_validation_success(
        self,
        request_data,
    ):
        request = self.factory.post(
            path='/handler',
            data=request_data,
            content_type='application/json',
        )
        response = await self.handler(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_api_view_schema_complex_validation_success(self):
        request = self.factory.post(
            path='/test_path/',
            data={'username': 'test', 'password': 'strong'},
            content_type='application/json',
        )
        response = await self.handler_with_complex_schema(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand(
        [
            (
                {'username': 'test', 'password': 'strong'},
                '/wrong_path/',
                'path is not "/test_path/"',
            ),
            (
                {'username': 'te', 'password': 'strong'},
                '/test_path/',
                'username is too short',
            ),
            param(
                {'username': 'test', 'password': 'not_strong'},
                '/test_path/',
                'password is invalid',
                status_code=HTTPStatus.UNAUTHORIZED,
            ),
        ],
    )
    async def test_api_view_schema_validation_failure(
        self,
        request_data,
        path,
        error_description,
        status_code=HTTPStatus.BAD_REQUEST,
    ):
        request = self.factory.post(
            path=path,
            data=request_data,
            content_type='application/json',
        )
        response = await self.handler_with_complex_schema(request)
        self.assertEqual(response.status_code, status_code)
        content = json.loads(response.content)
        self.assertEqual(content['error'], error_description)


class APIViewAuthenticationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()

        @api_view(methods=['GET'], login_required=True)
        async def handler(request):
            return JsonResponse({}, status=HTTPStatus.OK)

        cls.handler = handler
        cls.user = User.objects.create_user(
            email='test',
            password='password',
        )

    async def test_authenticated_user_has_access(self):
        request = self.factory.get(path='/handler')

        # in real cases user_id is set at JWTAuthenticationMiddleware level
        request.user_id = 123

        response = await self.handler(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    async def test_anonymous_user_has_no_access(self):
        request = self.factory.get(path='/handler')

        response = await self.handler(request)
        error = json.loads(response.content)['error']

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(error, 'authentication required')
