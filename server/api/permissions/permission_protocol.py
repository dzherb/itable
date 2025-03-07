import typing

from django.http import HttpRequest


class Permission(typing.Protocol):
    async def has_permission(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> bool: ...
