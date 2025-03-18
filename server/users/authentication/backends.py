import typing

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from users.authentication import exceptions
from users.authentication.jwt import (
    JWT,
    JWTPayloadValidator,
    PyJWT,
    PyJWTPayloadValidator,
    TokenPayload,
)
from users.models import ItableUser

User = get_user_model()


class JWTAuthenticationBackend(ModelBackend):
    AUTH_HEADER_PREFIX = 'Token'
    JWT_FACTORY: type[JWT] = PyJWT
    JWT_PAYLOAD_VALIDATOR: type[JWTPayloadValidator] = PyJWTPayloadValidator

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: typing.Any,
    ) -> ItableUser | None:
        if request is not None and self._has_auth_header(request):
            payload = self.authenticate_from_header(request)
        elif access_token := kwargs.get('access_token'):
            payload = self.check_token(access_token)
        else:
            return None

        try:
            return User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist as e:
            raise PermissionDenied from e

    def _has_auth_header(self, request: HttpRequest) -> bool:
        return request.headers.get('Authorization') is not None

    def authenticate_from_header(self, request: HttpRequest) -> TokenPayload:
        try:
            auth_header = request.headers['Authorization']
        except KeyError as e:
            raise PermissionDenied from e

        try:
            auth_prefix, access_token = auth_header.split(' ')
        except ValueError as e:
            raise PermissionDenied from e

        if auth_prefix != self.AUTH_HEADER_PREFIX:
            raise PermissionDenied

        return self.check_token(access_token)

    def check_token(self, access_token: str) -> TokenPayload:
        try:
            payload: TokenPayload = self.JWT_FACTORY().decode_token(
                access_token,
            )
        except exceptions.InvalidTokenError as e:
            raise PermissionDenied from e

        if not self.JWT_PAYLOAD_VALIDATOR().is_valid(payload):
            raise PermissionDenied

        return payload

    async def aget_user(self, user_id: int) -> ItableUser | None:
        return await sync_to_async(self.get_user)(user_id)
