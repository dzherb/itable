from datetime import datetime
from typing import assert_never, cast, Literal

from django.conf import settings
from django.utils import timezone
import jwt

ALGORITHM = 'HS256'


type JSONDict = dict[str, str | int | float | bool | list[str]]


def issue_token(
    data: JSONDict,
    token_type: Literal['access', 'refresh'],
    scopes: list[str] | None = None,
) -> str:
    if scopes is None:
        scopes = []

    issued_at = timezone.now()
    expires_at: datetime

    if token_type == 'access':
        expires_at = issued_at + settings.ACCESS_TOKEN_TIME_TO_LIVE
    elif token_type == 'refresh':
        expires_at = issued_at + settings.REFRESH_TOKEN_TIME_TO_LIVE
    else:
        assert_never(token_type)

    to_encode: JSONDict = {
        'iat': issued_at.timestamp(),
        'exp': expires_at.timestamp(),
        'type': token_type,
        'scopes': scopes,
    }

    to_encode.update(data)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> JSONDict:
    data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    return cast(JSONDict, data)
