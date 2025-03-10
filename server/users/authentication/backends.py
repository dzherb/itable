import typing

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
        if request is None:
            return None

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            auth_prefix, access_token = auth_header.split(' ')
        except ValueError as e:
            raise PermissionDenied from e

        if auth_prefix != self.AUTH_HEADER_PREFIX:
            raise PermissionDenied from None

        try:
            payload: TokenPayload = self.JWT_FACTORY().decode_token(
                access_token,
            )
        except exceptions.InvalidTokenError:
            raise PermissionDenied from None

        if not self.JWT_PAYLOAD_VALIDATOR().is_valid(payload):
            raise PermissionDenied from None

        try:
            return User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist:
            raise PermissionDenied from None
