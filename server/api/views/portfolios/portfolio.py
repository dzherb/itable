from django.http import JsonResponse

from api.helpers import aget_object_or_404_json, Dispatcher
from api.permissions import IsPortfolioOwner
from api.views.api_view import api_view
from portfolio.models import Portfolio


@api_view(login_required=True, permissions=[IsPortfolioOwner()])
async def get_portfolio(request, pk: int):
    portfolio = await aget_object_or_404_json(Portfolio, pk=pk)
    return JsonResponse(portfolio.serialize())


portfolio_dispatcher = Dispatcher(get=get_portfolio)
