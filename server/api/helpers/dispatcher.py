from collections.abc import Sequence
import typing

from django.http import HttpRequest, HttpResponse

from api.request_checkers import MethodsChecker
from api.request_checkers.methods_checker import Methods
from api.typedefs import AsyncViewFunction


class _Handlers(typing.TypedDict, total=False):
    get: AsyncViewFunction
    post: AsyncViewFunction
    put: AsyncViewFunction
    patch: AsyncViewFunction
    delete: AsyncViewFunction


class Dispatcher:
    def __init__(self, **method_handlers: typing.Unpack[_Handlers]):
        for method_name, handler in method_handlers.items():
            setattr(self, method_name.lower(), handler)

        allowed_methods: Sequence[Methods] = tuple(
            typing.cast(Methods, method.upper())
            for method in method_handlers.keys()
        )
        self._methods_checker = MethodsChecker(allowed_methods)

    def as_view(self) -> AsyncViewFunction:
        async def dispatch(
            request: HttpRequest,
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> HttpResponse:
            if not await self._methods_checker.check(request):
                return self._methods_checker.on_failure_response()

            handler: AsyncViewFunction = getattr(
                self,
                str(request.method).lower(),
            )
            return await handler(
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
