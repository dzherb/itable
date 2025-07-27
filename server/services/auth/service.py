from collections.abc import Iterable
from datetime import datetime
import hashlib
from http import HTTPStatus
from typing import Final, TYPE_CHECKING

from django.contrib.auth import aauthenticate, get_user_model
from django.utils import timezone
from jwt import ExpiredSignatureError, InvalidTokenError
from ninja.errors import HttpError
from pydantic import ValidationError

from cache.core import cache
from schemas.auth import (
    AccessToken,
    BaseToken,
    RefreshToken,
    TokenPair,
)
from services.auth.tokens import (
    decode_token,
    issue_token,
    JSONDict,
)

if TYPE_CHECKING:
    from apps.users.models import ItableUser

User = get_user_model()


class AuthError(HttpError):
    pass


async def login_user(
    email: str,
    password: str,
    scopes: list[str] | None = None,
) -> TokenPair:
    user = await aauthenticate(email=email, password=password)
    if user is None:
        raise AuthError(
            message='Incorrect username or password',
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    token_pair = await _issue_token_pair(user, scopes)

    user.last_login = timezone.now()
    await user.asave(update_fields=['last_login'])

    return token_pair


JWT_BLACKLIST_PREFIX: Final = 'jwt:blacklist'


async def refresh_tokens(
    refresh_token: str,
) -> TokenPair:
    # Check if token is valid before any request to cache or db,
    token_data = _decode_and_get_token_data(refresh_token, RefreshToken)

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    if cache.get(f'{JWT_BLACKLIST_PREFIX}:{token_hash}') is not None:
        raise AuthError(
            message='Token is disposed',
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    user = await User.objects.active().filter(id=token_data.sub).afirst()
    if user is None:
        raise AuthError(
            message='User not found',
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    token_pair = await _issue_token_pair(
        user,
        # Make scopes the same as for the previous token
        scopes=token_data.scopes,
    )

    # This token is used, now dispose it
    await cache.set(
        key=f'{JWT_BLACKLIST_PREFIX}:{token_hash}',
        value=refresh_token,
        expires_at=datetime.fromtimestamp(
            timestamp=token_data.exp,
            tz=timezone.get_current_timezone(),
        ),
    )

    return token_pair


def authenticate_and_decode_token(
    required_scopes: Iterable[str],
    token: str,
) -> AccessToken:
    token_data = _decode_and_get_token_data(token, AccessToken)
    for scope in required_scopes:
        if scope not in token_data.scopes:
            raise AuthError(
                message='Invalid scope',
                status_code=HTTPStatus.FORBIDDEN,
            )

    return token_data


async def get_available_scopes_for_user(user: 'ItableUser') -> list[str]:
    scopes: list[str] = []
    if user.is_superuser:
        scopes.append('admin')

    return scopes


def _decode_and_get_token_data[T: BaseToken](token: str, model: type[T]) -> T:
    try:
        return model.model_validate(decode_token(token))
    except ExpiredSignatureError as e:
        raise AuthError(
            message='Token is expired',
            status_code=HTTPStatus.UNAUTHORIZED,
        ) from e
    except (InvalidTokenError, ValidationError) as e:
        raise AuthError(
            message='Token is invalid',
            status_code=HTTPStatus.UNAUTHORIZED,
        ) from e


async def _issue_token_pair(
    user: 'ItableUser',
    scopes: list[str] | None = None,
) -> TokenPair:
    payload: JSONDict = {'sub': str(user.id)}

    available_scopes = await get_available_scopes_for_user(user)
    result_scopes: list[str] = []

    if scopes is not None:
        result_scopes.extend(list(set(scopes) & set(available_scopes)))

    access_token = issue_token(
        data=payload,
        token_type='access',
        scopes=result_scopes,
    )
    refresh_token = issue_token(
        data=payload,
        token_type='refresh',
        scopes=result_scopes,
    )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )
