import typing

from django.http import HttpRequest, HttpResponse


class Checker(typing.Protocol):
    async def check(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> bool: ...
    def on_failure_response(self) -> HttpResponse: ...
