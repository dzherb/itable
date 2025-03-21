import logging

from django.contrib import auth
from django.http import HttpRequest, HttpResponse, JsonResponse

from api.views.api_view import api_view

logger = logging.getLogger('api')


@api_view(methods=['POST'])
async def logout(request: HttpRequest) -> HttpResponse:
    await auth.alogout(request)
    logger.info('User logged out', extra={'user_id': request.user.id})
    return JsonResponse({})
