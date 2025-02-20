import asyncio
from collections.abc import Iterable, Sequence
import functools
from http import HTTPStatus
import typing
from typing import Callable, Literal, override

from django.http import HttpRequest, HttpResponse, JsonResponse

from api.permissions.permission_protocol import Permission

Methods = Literal['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']


class Checker(typing.Protocol):
    async def check(self, request: HttpRequest) -> bool: ...
    def on_failure_response(self) -> HttpResponse: ...


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


class api_view:  # noqa: N801
    DEFAULT_HTTP_METHOD: Methods = 'GET'

    def __new__(
        cls,
        view_function: Callable | None = None,
        **kwargs,
    ) -> Callable:
        self = super().__new__(cls)
        self._init(**kwargs)

        if (
            view_function is not None
            and callable(view_function)
            and len(kwargs) == 0
        ):
            return self.__call__(view_function)

        return self

    def _init(
        self,
        *,
        methods: Sequence[Methods] | None = None,
        permissions: Iterable[Permission] | None = None,
        checkers: Iterable[Checker] | None = None,
    ):
        self._methods = methods
        self._permissions = permissions
        self._checkers = checkers

    def __init__(
        self,
        *,
        methods: Sequence[Methods] | None = None,
        permissions: Iterable[Permission] | None = None,
        checkers: Iterable[Checker] | None = None,
    ):
        # We don't really need this method,
        # but without it, we lose type checking.
        pass

    def __call__(self, decorated_function: Callable) -> Callable:
        @functools.wraps(decorated_function)
        async def wrapped_f(
            request: HttpRequest,
            *args,
            **kwargs,
        ) -> HttpResponse:
            checks_result = await self._apply_checks(request)
            if checks_result is not None:
                return checks_result

            return await decorated_function(request, *args, **kwargs)

        return wrapped_f

    async def _apply_checks(self, request: HttpRequest) -> HttpResponse | None:
        for checker in self._get_checkers():
            if not await checker.check(request):
                return checker.on_failure_response()

        return None

    def _get_checkers(self):
        checkers = []
        if self._methods is not None:
            checkers.append(MethodsChecker(self._methods))
        else:
            checkers.append(MethodsChecker([self.DEFAULT_HTTP_METHOD]))

        if self._permissions is not None:
            checkers.append(PermissionsChecker(self._permissions))

        if self._checkers is not None:
            checkers += self._checkers

        return checkers
