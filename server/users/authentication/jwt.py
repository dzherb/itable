import datetime as dt
import typing

from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware
import jwt

from users.authentication.exceptions import InvalidTokenError


class TokenPayload(typing.TypedDict):
    uid: int
    exp: float


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


class JWTPayloadChecker(typing.Protocol):
    def is_active(self, payload: TokenPayload) -> bool: ...


class PyJWT(JWT):
    __slots__ = ('_algorithm',)

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

    def _generate_token(self, user_id: int, ttl: dt.timedelta) -> str:
        payload: TokenPayload = {
            'uid': user_id,
            'exp': (timezone.now() + ttl).timestamp(),
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


class PyJWTPayloadChecker(JWTPayloadChecker):
    def is_active(self, payload: TokenPayload) -> bool:
        now = timezone.now()
        timestamp = payload['exp']
        return make_aware(dt.datetime.fromtimestamp(timestamp)) >= now
