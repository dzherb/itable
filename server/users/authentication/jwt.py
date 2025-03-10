import datetime
import typing

from django.conf import settings
from django.utils import timezone
import jwt

from users.authentication.exceptions import InvalidTokenError


class TokenPayload(typing.TypedDict):
    user_id: int
    expires_at: str  # iso


class AccessTokenPayload(TokenPayload):
    pass


class RefreshTokenPayload(TokenPayload):
    pass


class TokenPair(typing.NamedTuple):
    access_token: str
    refresh_token: str


class JWT(typing.Protocol):
    def generate_tokens(self, user_id: int) -> TokenPair: ...

    def decode_token(self, token: str) -> TokenPayload: ...


class JWTPayloadValidator(typing.Protocol):
    def is_valid(self, payload: TokenPayload) -> bool: ...


class PyJWT(JWT):
    def __init__(self) -> None:
        self._algorithm = 'HS256'

    def generate_tokens(self, user_id: int) -> TokenPair:
        return TokenPair(
            access_token=self._generate_token(
                user_id,
                settings.ACCESS_TOKEN_TIME_TO_LIVE,
            ),
            refresh_token=self._generate_token(
                user_id,
                settings.REFRESH_TOKEN_TIME_TO_LIVE,
            ),
        )

    def _generate_token(self, user_id: int, ttl: datetime.timedelta) -> str:
        payload: TokenPayload = {
            'user_id': user_id,
            'expires_at': (timezone.now() + ttl).isoformat(),
        }
        return jwt.encode(
            payload=typing.cast(dict[str, typing.Any], payload),
            key=settings.SECRET_KEY,
            algorithm=self._algorithm,
        )

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=[self._algorithm],
            )
            return typing.cast(TokenPayload, payload)
        except jwt.exceptions.InvalidTokenError as e:
            raise InvalidTokenError from e


class PyJWTPayloadValidator(JWTPayloadValidator):
    def is_valid(self, payload: TokenPayload) -> bool:
        now = timezone.now()
        if datetime.datetime.fromisoformat(payload['expires_at']) < now:
            return False

        return True
