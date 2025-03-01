from collections.abc import Coroutine
import typing

from django.http import HttpRequest, HttpResponse

import users.models

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance


class AsyncViewFunction[T: HttpRequest](typing.Protocol):
    def __call__(
        self,
        request: T,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Coroutine[typing.Any, typing.Any, HttpResponse]: ...


class AuthenticatedRequest(HttpRequest):
    user: users.models.ItableUser


class PopulatedSchemaRequest[T: 'DataclassInstance'](HttpRequest):
    populated_schema: T


class AuthenticatedPopulatedSchemaRequest[T: 'DataclassInstance'](
    AuthenticatedRequest,
    PopulatedSchemaRequest[T],
):
    pass
