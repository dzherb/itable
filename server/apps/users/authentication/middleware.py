from collections.abc import Awaitable, Callable
import functools
import typing

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from api.typedefs import AuthenticatedRequest
from apps.users.authentication.backends import JWTAuthenticationBackend
from apps.users.authentication.jwt import TokenPayload
from apps.users.models import ItableUser


class JWTAuthenticationMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(
        self,
        get_response: Callable[[HttpRequest], Awaitable[HttpResponse]],
    ) -> None:
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            payload: TokenPayload = (
                JWTAuthenticationBackend().authenticate_from_header(request)
            )
            request = typing.cast(AuthenticatedRequest, request)
            request.user_id = payload['uid']
        except PermissionDenied:
            pass

        request.auser = functools.partial(auser, request)

        return await self.get_response(request)


class CachedUserRequests(HttpRequest):
    _acached_user: ItableUser | AnonymousUser


async def auser(
    request: HttpRequest | AuthenticatedRequest,
) -> ItableUser | AnonymousUser:
    request = typing.cast(CachedUserRequests, request)

    if not hasattr(request, '_acached_user'):
        user: ItableUser | AnonymousUser
        user_id: int | None = getattr(request, 'user_id', None)
        if not user_id:
            request._acached_user = AnonymousUser()
        else:
            maybe_user = await JWTAuthenticationBackend().aget_user(user_id)
            user = AnonymousUser() if maybe_user is None else maybe_user
            request._acached_user = user

    return request._acached_user
