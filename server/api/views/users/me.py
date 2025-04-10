import dataclasses

from django.http import HttpResponse, JsonResponse

from api.helpers.api_view import api_view
from api.helpers.model_converters import ModelToDictConverter
from api.typedefs import AuthenticatedRequest


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
