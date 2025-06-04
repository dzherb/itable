import logging

from django.http import HttpResponse, JsonResponse

from api.core.api_view import api_view
from api.permissions import IsPortfolioOwner
from api.typedefs import (
    AuthenticatedPopulatedSchemaRequest,
    AuthenticatedRequest,
)
from api.utils.dispatcher import create_dispatcher
from schemas.portfolio import (
    PortfolioCreateSchema,
    PortfolioListSchema,
    PortfolioSchema,
    PortfolioUpdateSchema,
)
from services.portfolios.service import PortfolioService

logger = logging.getLogger('api')


@api_view(
    methods=['GET'],
    login_required=True,
    permissions=[IsPortfolioOwner()],
)
async def get_portfolio(
    request: AuthenticatedRequest,
    pk: int,
) -> HttpResponse:
    portfolio: PortfolioSchema = await PortfolioService().get_portfolio(pk)
    return JsonResponse(portfolio.model_dump())


@api_view(
    methods=['POST'],
    login_required=True,
    request_schema=PortfolioCreateSchema,
)
async def create_portfolio(
    request: AuthenticatedPopulatedSchemaRequest[PortfolioCreateSchema],
) -> HttpResponse:
    portfolio: PortfolioSchema = await PortfolioService().create_portfolio(
        request.populated_schema,
        request.user_id,
    )
    return JsonResponse(portfolio.model_dump())


@api_view(
    methods=['DELETE'],
    login_required=True,
    permissions=[IsPortfolioOwner()],
)
async def delete_portfolio(
    request: AuthenticatedRequest,
    pk: int,
) -> HttpResponse:
    await PortfolioService().delete_portfolio(pk)
    return JsonResponse({})


@api_view(
    methods=['PATCH'],
    login_required=True,
    permissions=[IsPortfolioOwner()],
    request_schema=PortfolioUpdateSchema,
)
async def update_portfolio(
    request: AuthenticatedPopulatedSchemaRequest[PortfolioUpdateSchema],
    pk: int,
) -> HttpResponse:
    portfolio = await PortfolioService().update_portfolio(
        pk,
        request.populated_schema,
    )

    return JsonResponse(portfolio.model_dump())


detail_dispatcher = create_dispatcher(
    get=get_portfolio,
    delete=delete_portfolio,
    patch=update_portfolio,
)


@api_view(methods=['GET'], login_required=True)
async def portfolio_list(request: AuthenticatedRequest) -> HttpResponse:
    portfolios: PortfolioListSchema = (
        await PortfolioService().get_user_portfolios(
            request.user_id,
        )
    )

    return JsonResponse(portfolios.model_dump())


dispatcher = create_dispatcher(
    get=portfolio_list,
    post=create_portfolio,
)
