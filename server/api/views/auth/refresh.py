import dataclasses

from django.http import HttpResponse, JsonResponse

from api.typedefs import (
    AuthenticatedPopulatedSchemaRequest,
    AuthenticatedRequest,
)
from api.views.api_view import api_view
from users.authentication.exceptions import InvalidTokenError
from users.authentication.jwt import (
    PyJWT,
    PyJWTPayloadValidator,
    TokenPair,
)


@dataclasses.dataclass
class RefreshTokenSchema:
    refresh_token: str

    async def validate(self, request: AuthenticatedRequest) -> None:
        try:
            payload = PyJWT().decode_token(self.refresh_token)
        except InvalidTokenError as e:
            raise ValueError('token is not valid') from e

        try:
            PyJWTPayloadValidator().is_valid(payload)
        except InvalidTokenError as e:
            raise ValueError('token is expired') from e

        if not (await request.auser()).can_refresh_tokens(self.refresh_token):
            raise ValueError('token is no longer active')


@api_view(
    methods=['POST'],
    login_required=True,
    request_schema=RefreshTokenSchema,
)
async def refresh_token(
    request: AuthenticatedPopulatedSchemaRequest[RefreshTokenSchema],
) -> HttpResponse:
    token_pair: TokenPair = await (await request.auser()).generate_new_tokens()
    return JsonResponse(
        {
            'access_token': token_pair.access_token,
            'refresh_token': token_pair.refresh_token,
        },
    )
