import dataclasses

from django.http import HttpResponse, JsonResponse

from api.typedefs import AuthenticatedPopulatedSchemaRequest
from api.views.api_view import api_view
from exchange.exchange.stock_markets import MOEX


@dataclasses.dataclass
class TickersSchema:
    tickers: list[str]


@api_view(
    methods=['GET'],
    login_required=True,
    request_schema=TickersSchema,
)
async def security_list(
    request: AuthenticatedPopulatedSchemaRequest[TickersSchema],
) -> HttpResponse:
    tickers: list[str] = request.populated_schema.tickers
    securities_from_moex = await MOEX().get_securities(tickers=tickers)
    return JsonResponse({'securities': securities_from_moex})
