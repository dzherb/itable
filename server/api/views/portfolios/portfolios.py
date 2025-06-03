import dataclasses
import datetime
import logging
import typing

from django.http import HttpResponse, JsonResponse

from api.core.api_view import api_view
from api.permissions import IsPortfolioOwner
from api.typedefs import (
    AuthenticatedPopulatedSchemaRequest,
    AuthenticatedRequest,
)
from api.utils import aget_object_or_404_json
from api.utils.converters import (
    ModelToDataclassConverter,
    ModelToDictConverter,
)
from api.utils.dispatcher import create_dispatcher
from api.utils.schema_mixins import ValidateNameSchemaMixin
from apps.portfolios.models import Portfolio

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


async def _serialize_portfolio(portfolio: Portfolio) -> dict[str, typing.Any]:
    converter = ModelToDictConverter(
        source=portfolio,
        schema=PortfolioSchema,
        skip_fields=('securities',),
    )
    serialized_portfolio = await converter.convert()
    return typing.cast(dict[str, typing.Any], serialized_portfolio)


async def _serialize_portfolio_with_securities(
    portfolio: Portfolio,
) -> dict[str, typing.Any]:
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
    serialized_portfolio = await converter.convert()
    return typing.cast(dict[str, typing.Any], serialized_portfolio)


@api_view(login_required=True, permissions=[IsPortfolioOwner()])
async def get_portfolio(
    request: AuthenticatedRequest,
    pk: int,
) -> HttpResponse:
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
async def create_portfolio(
    request: AuthenticatedPopulatedSchemaRequest[
        PortfolioCreateAndUpdateSchema
    ],
) -> HttpResponse:
    portfolio: Portfolio = await Portfolio.objects.acreate(
        name=request.populated_schema.name,
        owner_id=request.user_id,
    )
    return JsonResponse(await _serialize_portfolio(portfolio))


@api_view(login_required=True, permissions=[IsPortfolioOwner()])
async def delete_portfolio(
    request: AuthenticatedRequest,
    pk: int,
) -> HttpResponse:
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
async def update_portfolio(
    request: AuthenticatedPopulatedSchemaRequest[
        PortfolioCreateAndUpdateSchema
    ],
    pk: int,
) -> HttpResponse:
    portfolio: Portfolio = await aget_object_or_404_json(
        Portfolio.objects.active().prefetch_items(),
        pk=pk,
    )
    portfolio.name = request.populated_schema.name
    await portfolio.asave(update_fields=['name'])
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
async def portfolio_list(request: AuthenticatedRequest) -> HttpResponse:
    select_fields = tuple(PortfolioListItemSchema.__dataclass_fields__.keys())
    user_portfolios = Portfolio.objects.filter(
        owner_id=request.user_id,
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
