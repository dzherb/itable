import dataclasses
from http import HTTPStatus
import json
from typing import override

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import AsyncRequestFactory, TestCase

from api.permissions.permission_protocol import Permission
from api.views.api_view import api_view, Checker

User = get_user_model()


class UsernameLenIs10Permission(Permission):
    @override
    async def check(self, request: HttpRequest) -> bool:
        return (
            request.user.is_authenticated and len(request.user.username) == 10
        )


class RequestHasAcceptCharsetHeaderChecker(Checker):
    @override
    async def check(self, request: HttpRequest) -> bool:
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

        request = self.factory.get('/hello_world')
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(content['message'], 'hello world')

    async def test_api_view_can_be_applied_with_arguments(self):
        @api_view(methods=['GET'])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get('/hello_world')
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(content['message'], 'hello world')

    async def test_api_view_checks_allowed_methods(self):
        @api_view(methods=['POST'])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get('/hello_world')
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(content['error'], 'Method not allowed')

    async def test_api_view_checks_permissions_and_not_allows(self):
        @api_view(permissions=[UsernameLenIs10Permission()])
        async def hello_world(request):
            return JsonResponse({'message': 'hello world'})

        request = self.factory.get('/hello_world')
        request.user = self.user
        response = await hello_world(request)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(content['error'], 'Permission denied')

    async def test_api_view_checks_permissions_and_allows(self):
        class UsernameLenIs4Permission(Permission):
            @override
            async def check(self, request: HttpRequest) -> bool:
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
            '/hello_world',
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


@dataclasses.dataclass
class UserLoginSchema:
    username: str
    password: str
    age: int | None


class APIViewSchemaTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = AsyncRequestFactory()

        @api_view(methods=['POST'], request_schema=UserLoginSchema)
        async def echo(request):
            user_login = request.populated_schema
            return JsonResponse(dataclasses.asdict(user_login))

        cls.echo_handler = echo

    async def test_request_body_populates_the_schema(self):
        valid_request_data = [
            {'username': 'test_user', 'password': 'password'},
            {'username': 'test_user', 'password': 'password', 'age': 20},
        ]

        for request_data in valid_request_data:
            with self.subTest(request_data=request_data):
                request = self.factory.post(
                    '/echo',
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
                    '/echo',
                    data=request_data,
                    content_type='application/json',
                )
                response = await self.echo_handler(request)
                content = json.loads(response.content)

                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertIn('error', content)
