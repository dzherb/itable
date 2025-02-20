import typing


class Permission(typing.Protocol):
    async def check(self, request) -> bool: ...
