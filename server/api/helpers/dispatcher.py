from collections.abc import Sequence
import typing

from django.http import HttpRequest, HttpResponse

from api.request_checkers import MethodsChecker
from api.typedefs import AsyncViewFunction


class _Handlers(typing.TypedDict):
    get: typing.NotRequired[AsyncViewFunction]
    post: typing.NotRequired[AsyncViewFunction]
    put: typing.NotRequired[AsyncViewFunction]
    patch: typing.NotRequired[AsyncViewFunction]
    delete: typing.NotRequired[AsyncViewFunction]


class Dispatcher:
    def __init__(self, **method_handlers: typing.Unpack[_Handlers]):
        for method_name, handler in method_handlers.items():
            setattr(self, method_name.lower(), handler)

        allowed_methods: Sequence = tuple(
            method.upper() for method in method_handlers.keys()
        )
        self._methods_checker = MethodsChecker(allowed_methods)

    def as_view(self):
        async def dispatch(
            request: HttpRequest,
            *args,
            **kwargs,
        ) -> HttpResponse:
            if not await self._methods_checker.check(request):
                return self._methods_checker.on_failure_response()

            return await getattr(self, str(request.method).lower())(
                request,
                *args,
                **kwargs,
            )

        return dispatch


def create_dispatcher(
    **method_handlers: typing.Unpack[_Handlers],
) -> AsyncViewFunction:
    dispatcher = Dispatcher(**method_handlers)
    return dispatcher.as_view()
