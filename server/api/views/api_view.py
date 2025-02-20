from collections.abc import Iterable, Sequence
import functools
from http import HTTPStatus
from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse

from api import exceptions
from api.permissions.permission_protocol import Permission
from api.request_checkers import (
    AuthenticationChecker,
    MethodsChecker,
    PermissionsChecker,
    SchemaChecker,
)
from api.request_checkers.checker_protocol import Checker
from api.request_checkers.methods_checker import Methods


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
        login_required: bool = False,
        permissions: Iterable[Permission] | None = None,
        request_schema: type | None = None,
        checkers: Iterable[Checker] | None = None,
    ):
        self._methods = methods
        self._login_required = login_required
        self._permissions = permissions
        self._user_checkers = checkers
        self._request_schema = request_schema

        # Collect checkers on init so we don't have to
        # do this on every decorated function call
        self._all_checkers = self._get_checkers()

    def __init__(
        self,
        *,
        methods: Sequence[Methods] | None = None,
        login_required: bool = False,
        permissions: Iterable[Permission] | None = None,
        request_schema: type | None = None,
        checkers: Iterable[Checker] | None = None,
    ):
        # We don't really need this method,
        # but without it, we lose type checking.
        pass

    def __call__(self, decorated_function: Callable) -> Callable:
        @functools.wraps(decorated_function)
        async def wrapper(
            request: HttpRequest,
            *args,
            **kwargs,
        ) -> HttpResponse:
            try:
                checks_result = await self._apply_checks(
                    request,
                    *args,
                    **kwargs,
                )
                if checks_result is not None:
                    return checks_result

                return await decorated_function(request, *args, **kwargs)
            except exceptions.NotFoundError:
                # This way we can handle aget_object_or_404_json call
                return JsonResponse(
                    data={'error': 'not found'},
                    status=HTTPStatus.NOT_FOUND,
                )

        return wrapper

    async def _apply_checks(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse | None:
        for checker in self._all_checkers:
            if not await checker.check(request, *args, **kwargs):
                return checker.on_failure_response()

        return None

    def _get_checkers(self):
        checkers = []
        if self._methods is not None:
            checkers.append(MethodsChecker(self._methods))
        else:
            checkers.append(MethodsChecker([self.DEFAULT_HTTP_METHOD]))

        if self._login_required:
            checkers.append(AuthenticationChecker())

        if self._request_schema is not None:
            checkers.append(SchemaChecker(self._request_schema))

        if self._permissions is not None:
            checkers.append(PermissionsChecker(self._permissions))

        if self._user_checkers is not None:
            checkers += self._user_checkers

        return checkers
