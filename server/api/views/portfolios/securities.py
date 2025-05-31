import dataclasses
import datetime
from http import HTTPStatus
import logging
import typing

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse

from api.exceptions import NotFoundError
from api.helpers import aget_object_or_404_json
from api.helpers.api_view import api_view
from api.helpers.dispatcher import create_dispatcher
from api.helpers.model_converters import ModelToDictConverter
from api.permissions import IsPortfolioOwner
from api.request_checkers.schema_checker import PopulatedSchemaRequest
from api.typedefs import (
    AuthenticatedPopulatedSchemaRequest,
    AuthenticatedRequest,
)
from apps.exchange.models import Security
from apps.portfolios.models import PortfolioItem

logger = logging.getLogger('api')

PORTFOLIO_ITEM_404_NAME = 'portfolio security'


class PortfolioItemValidationMixin:
    quantity: int

    def validate_quantity(self) -> None:
        if self.quantity <= 0:
            raise ValueError('quantity must be greater than zero')


@dataclasses.dataclass(slots=True, frozen=True)
class PortfolioSecurityAddSchema(PortfolioItemValidationMixin):
    ticker: str
    quantity: int


@dataclasses.dataclass(slots=True, frozen=True)
class PortfolioSecurityUpdateSchema(PortfolioItemValidationMixin):
    quantity: int


@dataclasses.dataclass(slots=True, frozen=True)
class PortfolioSecuritySchema(PortfolioItemValidationMixin):
    portfolio_id: int
    ticker: str
    quantity: int
    created_at: datetime.datetime


async def _serialize_portfolio_item(
    item: PortfolioItem,
) -> dict[str, typing.Any]:
    converter = ModelToDictConverter(
        source=item,
        schema=PortfolioSecuritySchema,
        fields_map={
            'ticker': 'security__ticker',
        },
    )
    serialized_item = await converter.convert()
    return typing.cast(dict[str, typing.Any], serialized_item)


@api_view(
    methods=['POST'],
    login_required=True,
    permissions=[IsPortfolioOwner(argument_name='portfolio_id')],
    request_schema=PortfolioSecurityAddSchema,
)
async def add_portfolio_security(
    request: PopulatedSchemaRequest[PortfolioSecurityAddSchema],
    portfolio_id: int,
) -> HttpResponse:
    item_schema: PortfolioSecurityAddSchema = request.populated_schema

    try:
        security: Security = await Security.get_or_try_to_create_from_moex(
            ticker=item_schema.ticker,
        )
    except Security.DoesNotExist as e:
        raise NotFoundError(Security) from e

    try:
        portfolio_item: PortfolioItem = await PortfolioItem.objects.acreate(
            portfolio_id=portfolio_id,
            security=security,
        )
    except IntegrityError:
        logger.warning(
            'Client attempted to add the same portfolio security twice',
            extra={
                'user_id': request.user.id,
                'portfolio_id': portfolio_id,
                'ticker': item_schema.ticker,
            },
        )
        return JsonResponse(
            {'error': 'security already exists'},
            status=HTTPStatus.BAD_REQUEST,
        )

    return JsonResponse(await _serialize_portfolio_item(portfolio_item))


@api_view(
    login_required=True,
    permissions=[IsPortfolioOwner(argument_name='portfolio_id')],
    request_schema=PortfolioSecurityUpdateSchema,
)
async def update_portfolio_security(
    request: AuthenticatedPopulatedSchemaRequest[
        PortfolioSecurityUpdateSchema
    ],
    portfolio_id: int,
    security_ticker: int,
) -> HttpResponse:
    portfolio_item: PortfolioItem = await aget_object_or_404_json(
        PortfolioItem.objects.select_related('security').only(
            'portfolio_id',
            'quantity',
            'created_at',
            'security__ticker',
        ),
        portfolio__id=portfolio_id,
        security__ticker=security_ticker,
        object_error_name=PORTFOLIO_ITEM_404_NAME,
    )
    portfolio_item.quantity = request.populated_schema.quantity
    await portfolio_item.asave(update_fields=['quantity'])

    return JsonResponse(await _serialize_portfolio_item(portfolio_item))


@api_view(
    login_required=True,
    permissions=[IsPortfolioOwner(argument_name='portfolio_id')],
)
async def remove_portfolio_security(
    request: AuthenticatedRequest,
    portfolio_id: int,
    security_ticker: int,
) -> HttpResponse:
    portfolio_item: PortfolioItem = await aget_object_or_404_json(
        PortfolioItem.objects.only(),
        portfolio_id=portfolio_id,
        security__ticker=security_ticker,
        object_error_name=PORTFOLIO_ITEM_404_NAME,
    )
    await portfolio_item.adelete()
    logger.info(
        'User deleted portfolio item',
        extra={
            'user_id': request.user.id,
            'portfolio_id': portfolio_id,
            'ticker': security_ticker,
        },
    )

    return JsonResponse({})


dispatcher = create_dispatcher(
    patch=update_portfolio_security,
    delete=remove_portfolio_security,
)
