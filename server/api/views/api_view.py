from collections.abc import Iterable, Sequence
import functools
from http import HTTPStatus
import typing

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
from api.typedefs import AsyncViewFunction


class _ApiViewWrapper:
    def __init__(
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

    def __call__(self, view_function: AsyncViewFunction) -> AsyncViewFunction:
        @functools.wraps(view_function)
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

                return await view_function(request, *args, **kwargs)
            except exceptions.NotFoundError as e:
                # This way we can handle aget_object_or_404_json call
                return JsonResponse(
                    data={'error': e.message},
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

        if self._login_required:
            checkers.append(AuthenticationChecker())

        if self._request_schema is not None:
            checkers.append(SchemaChecker(self._request_schema))

        if self._permissions is not None:
            checkers.append(PermissionsChecker(self._permissions))

        if self._user_checkers is not None:
            checkers += self._user_checkers

        return checkers


@typing.overload
def api_view(
    view_function: AsyncViewFunction,
    /,
    *,
    methods: Sequence[Methods] | None = None,
    login_required: bool = False,
    permissions: Iterable[Permission] | None = None,
    request_schema: type | None = None,
    checkers: Iterable[Checker] | None = None,
) -> AsyncViewFunction: ...


@typing.overload
def api_view(
    view_function: None = None,
    /,
    *,
    methods: Sequence[Methods] | None = None,
    login_required: bool = False,
    permissions: Iterable[Permission] | None = None,
    request_schema: type | None = None,
    checkers: Iterable[Checker] | None = None,
) -> _ApiViewWrapper: ...


def api_view(
    view_function=None,
    /,
    *,
    methods=None,
    login_required=False,
    permissions=None,
    request_schema=None,
    checkers=None,
):
    if view_function is not None:
        assert callable(view_function)
        return _ApiViewWrapper()(view_function)

    return _ApiViewWrapper(
        methods=methods,
        login_required=login_required,
        permissions=permissions,
        request_schema=request_schema,
        checkers=checkers,
    )
