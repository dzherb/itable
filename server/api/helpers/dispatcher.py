from collections.abc import Callable, Sequence

from django.http import HttpRequest, HttpResponse

from api.request_checkers import MethodsChecker


class Dispatcher:
    def __init__(self, **method_handlers: Callable):
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

            return await getattr(self, request.method.lower())(
                request,
                *args,
                **kwargs,
            )

        return dispatch
