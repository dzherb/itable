import dataclasses

from django.http import HttpResponse, JsonResponse

from api.core.api_view import api_view
from api.typedefs import AuthenticatedRequest
from api.utils.converters import ModelToDictConverter


@dataclasses.dataclass
class UserSchema:
    id: int
    email: str


@api_view(login_required=True)
async def me(request: AuthenticatedRequest) -> HttpResponse:
    user = await request.auser()
    converter = ModelToDictConverter(
        source=user,
        schema=UserSchema,
    )
    return JsonResponse(await converter.convert())
