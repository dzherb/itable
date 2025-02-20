from http import HTTPStatus
from typing import override

from django.http import HttpRequest, HttpResponse, JsonResponse

from api.request_checkers.checker_protocol import Checker


class AuthenticationChecker(Checker):
    @override
    async def check(self, request: HttpRequest, *args, **kwargs) -> bool:
        user = await request.auser()
        request.user = user
        return user.is_authenticated

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': 'authentication required'},
            status=HTTPStatus.UNAUTHORIZED,
        )
