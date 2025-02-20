import typing

from django.http import HttpRequest, HttpResponse


class Checker(typing.Protocol):
    async def check(self, request: HttpRequest, *args, **kwargs) -> bool: ...
    def on_failure_response(self) -> HttpResponse: ...
