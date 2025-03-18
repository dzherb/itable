from collections.abc import Awaitable, Callable, Coroutine
import typing

from django.http import HttpRequest, HttpResponse

from users.models import ItableUser

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance


class AsyncViewFunction(typing.Protocol):
    def __call__(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Coroutine[typing.Any, typing.Any, HttpResponse]: ...


class ApiViewFunction[T: HttpRequest](typing.Protocol):
    def __call__(
        self,
        request: T,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Coroutine[typing.Any, typing.Any, HttpResponse]: ...


class AuthenticatedRequest(HttpRequest):
    user_id: int
    auser: Callable[[], Awaitable[ItableUser]]


class PopulatedSchemaRequest[T: 'DataclassInstance'](HttpRequest):
    populated_schema: T


class AuthenticatedPopulatedSchemaRequest[T: 'DataclassInstance'](
    AuthenticatedRequest,
    PopulatedSchemaRequest[T],
):
    pass
