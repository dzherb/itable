import logging

from django.http import HttpRequest, HttpResponse, JsonResponse

from api.helpers.api_view import api_view
from api.typedefs import AuthenticatedRequest

logger = logging.getLogger('api')


@api_view(methods=['POST'])
async def logout(request: HttpRequest | AuthenticatedRequest) -> HttpResponse:
    user = await request.auser()
    if user.is_authenticated:
        # make previous refresh token invalid
        await user.generate_new_tokens()

    logger.info(
        msg='User logged out',
        extra={'user_id': user.id} if user.is_authenticated else {},
    )
    return JsonResponse({})
