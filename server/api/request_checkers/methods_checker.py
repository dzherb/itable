from collections.abc import Sequence
from http import HTTPStatus
from typing import Literal, override

from django.http import HttpRequest, HttpResponse, JsonResponse

from api.request_checkers.checker_protocol import Checker

Methods = Literal['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']


class MethodsChecker(Checker):
    def __init__(self, methods: Sequence[Methods]):
        self._allowed_methods: Sequence[Methods] = methods

    @override
    async def check(self, request: HttpRequest) -> bool:
        return request.method in self._allowed_methods

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': 'Method not allowed'},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )
