import dataclasses

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse

from api.typedefs import (
    PopulatedSchemaRequest,
)
from api.views.api_view import api_view
from users.authentication.exceptions import InvalidTokenError
from users.authentication.jwt import (
    PyJWT,
    PyJWTPayloadValidator,
    TokenPair,
)
from users.models import ItableUser

User = get_user_model()


@dataclasses.dataclass
class RefreshTokenSchema:
    refresh_token: str
    user: ItableUser | None = None  # field is set after the validation

    async def validate_refresh_token(self) -> str:
        refresh_token: str = self.refresh_token
        try:
            payload = PyJWT().decode_token(refresh_token)
        except InvalidTokenError as e:
            raise ValueError('token is not valid') from e

        if not PyJWTPayloadValidator().is_valid(payload):
            raise ValueError('token is expired')

        user_id = payload['user_id']

        try:
            user = await User.objects.aget(pk=user_id)
        except User.DoesNotExist as e:
            raise ValueError('user does not exist') from e

        if not user.can_refresh_tokens(refresh_token):
            raise ValueError('token is no longer active')

        self.user = user
        return refresh_token


@api_view(
    methods=['POST'],
    request_schema=RefreshTokenSchema,
)
async def refresh_token(
    request: PopulatedSchemaRequest[RefreshTokenSchema],
) -> HttpResponse:
    user: ItableUser | None = request.populated_schema.user
    assert user is not None
    token_pair: TokenPair = await user.generate_new_tokens()
    return JsonResponse(
        {
            'access_token': token_pair.access_token,
            'refresh_token': token_pair.refresh_token,
        },
    )
