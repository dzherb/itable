import dataclasses
from http import HTTPStatus
import logging

from django.contrib import auth
from django.http import JsonResponse

from api.views.api_view import api_view

logger = logging.getLogger('api')


@dataclasses.dataclass
class UserCredentialsSchema:
    username: str
    password: str


@api_view(methods=['POST'], request_schema=UserCredentialsSchema)
async def login(request):
    user_credentials: UserCredentialsSchema = request.populated_schema
    user = await auth.aauthenticate(
        request,
        username=user_credentials.username,
        password=user_credentials.password,
    )

    if user is not None:
        await auth.alogin(request, user)
        logger.info('User logged in', extra={'user_id': user.id})
        return JsonResponse({})

    logger.info(
        'User failed to login',
        extra={'user_agent': request.headers.get('User-Agent')},
    )
    return JsonResponse(
        {'error': 'invalid credentials'},
        status=HTTPStatus.UNAUTHORIZED,
    )
