import dataclasses
import datetime
import logging

from django.http import JsonResponse

from api.helpers import aget_object_or_404_json
from api.helpers.dispatcher import create_dispatcher
from api.helpers.model_converters import (
    ModelToDataclassConverter,
    ModelToDictConverter,
)
from api.helpers.schema_mixins import ValidateNameSchemaMixin
from api.permissions import IsPortfolioOwner
from api.views.api_view import api_view
from portfolio.models import Portfolio

logger = logging.getLogger('api')


@dataclasses.dataclass
class PortfolioSecuritySchema:
    ticker: str
    quantity: int


@dataclasses.dataclass
class PortfolioSchema:
    id: int
    name: str
    owner_id: int
    created_at: datetime.datetime
    securities: list[PortfolioSecuritySchema]


@dataclasses.dataclass
class PortfolioCreateAndUpdateSchema(ValidateNameSchemaMixin):
    name: str


async def _serialize_portfolio(portfolio: Portfolio) -> dict:
    converter = ModelToDictConverter(
        source=portfolio,
        schema=PortfolioSchema,
        skip_fields=('securities',),
    )
    return await converter.convert()


async def _serialize_portfolio_with_securities(portfolio: Portfolio) -> dict:
    converter = ModelToDictConverter(
        source=portfolio,
        schema=PortfolioSchema,
        fields_map={
            'securities': ModelToDataclassConverter(
                source=portfolio.items.all(),
                schema=PortfolioSecuritySchema,
                fields_map={'ticker': 'security__ticker'},
                many=True,
            ),
        },
    )
    return await converter.convert()


@api_view(login_required=True, permissions=[IsPortfolioOwner()])
async def get_portfolio(request, pk: int):
    portfolio: Portfolio = await aget_object_or_404_json(
        Portfolio.objects.active().prefetch_items(),
        pk=pk,
    )
    return JsonResponse(await _serialize_portfolio_with_securities(portfolio))


@api_view(
    methods=['POST'],
    login_required=True,
    request_schema=PortfolioCreateAndUpdateSchema,
)
async def create_portfolio(request):
    portfolio_schema: PortfolioCreateAndUpdateSchema = request.populated_schema
    portfolio: Portfolio = await Portfolio.objects.acreate(
        name=portfolio_schema.name,
        owner=request.user,
    )
    return JsonResponse(await _serialize_portfolio(portfolio))


@api_view(login_required=True, permissions=[IsPortfolioOwner()])
async def delete_portfolio(request, pk: int):
    portfolio: Portfolio = await aget_object_or_404_json(
        Portfolio.objects.active().only(),
        pk=pk,
    )
    portfolio.is_active = False
    await portfolio.asave()
    logger.info(
        'User deleted a portfolio',
        extra={'portfolio_id': portfolio.id, 'user_id': request.user.id},
    )
    return JsonResponse({})


@api_view(
    login_required=True,
    permissions=[IsPortfolioOwner()],
    request_schema=PortfolioCreateAndUpdateSchema,
)
async def update_portfolio(request, pk: int):
    portfolio: Portfolio = await aget_object_or_404_json(
        Portfolio.objects.active().prefetch_items(),
        pk=pk,
    )
    portfolio.name = request.populated_schema.name
    await portfolio.asave()
    return JsonResponse(await _serialize_portfolio_with_securities(portfolio))


detail_dispatcher = create_dispatcher(
    get=get_portfolio,
    delete=delete_portfolio,
    patch=update_portfolio,
)


@dataclasses.dataclass
class PortfolioListItemSchema:
    id: int
    name: str
    owner_id: int
    created_at: datetime.datetime


@api_view(methods=['GET'], login_required=True)
async def portfolio_list(request):
    select_fields = tuple(PortfolioListItemSchema.__dataclass_fields__.keys())
    user_portfolios = Portfolio.objects.filter(
        owner_id=request.user.id,
    ).only(*select_fields)

    converter = ModelToDictConverter(
        source=user_portfolios,
        schema=PortfolioListItemSchema,
        many=True,
    )
    portfolios = await converter.convert()
    return JsonResponse({'portfolios': portfolios})


dispatcher = create_dispatcher(
    get=portfolio_list,
    post=create_portfolio,
)
