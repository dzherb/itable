from http import HTTPStatus
import typing
from typing import override

from django.http import HttpRequest, HttpResponse, JsonResponse

from api.request_checkers.checker_protocol import Checker


class AuthenticationChecker(Checker):
    @override
    async def check(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> bool:
        return bool(getattr(request, 'user_id', False))

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': 'authentication required'},
            status=HTTPStatus.UNAUTHORIZED,
        )
