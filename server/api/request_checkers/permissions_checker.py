import asyncio
from collections.abc import Iterable
from http import HTTPStatus
from typing import override

from django.http import HttpRequest, HttpResponse, JsonResponse

from api.permissions.permission_protocol import Permission
from api.request_checkers.checker_protocol import Checker


class PermissionsChecker(Checker):
    """
    Applies permissions checks.
    It doesn't guarantee to follow the order in which permissions were passed.
    """

    def __init__(self, permissions: Iterable[Permission]):
        self._permissions = permissions

    @override
    async def check(self, request: HttpRequest) -> bool:
        tasks = [permission.check(request) for permission in self._permissions]
        for result in asyncio.as_completed(tasks):
            if not await result:
                return False

        return True

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': 'Permission denied'},
            status=HTTPStatus.FORBIDDEN,
        )
