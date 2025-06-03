from http import HTTPStatus
import logging

from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from pydantic import BaseModel

from api.helpers.api_view import api_view
from api.request_checkers.schema_checker import PopulatedSchemaRequest
from apps.users.authentication.jwt import TokenPair
from apps.users.models import ItableUser

logger = logging.getLogger('api')


class UserCredentialsSchema(BaseModel):
    email: str
    password: str


@api_view(methods=['POST'], request_schema=UserCredentialsSchema)
async def login(
    request: PopulatedSchemaRequest[UserCredentialsSchema],
) -> HttpResponse:
    user_credentials: UserCredentialsSchema = request.populated_schema
    user: ItableUser | None = await auth.aauthenticate(
        None,
        email=user_credentials.email,
        password=user_credentials.password,
    )

    if user is not None:
        logger.info('User logged in', extra={'user_id': user.id})
        token_pair: TokenPair = await user.generate_new_tokens()
        return JsonResponse(
            {
                'access_token': token_pair.access_token,
                'refresh_token': token_pair.refresh_token,
            },
        )

    logger.info(
        'User failed to login',
        extra={'user_agent': request.headers.get('User-Agent')},
    )
    return JsonResponse(
        {'error': 'invalid credentials'},
        status=HTTPStatus.UNAUTHORIZED,
    )
