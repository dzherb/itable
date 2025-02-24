import dataclasses
import datetime
from http import HTTPStatus
import logging

from django.db import IntegrityError
from django.http import JsonResponse

from api.helpers import aget_object_or_404_json
from api.helpers.dispatcher import create_dispatcher
from api.helpers.model_converters import ModelToDictConverter
from api.permissions import IsPortfolioOwner
from api.views.api_view import api_view
from exchange.models import Security
from portfolio.models import PortfolioItem

logger = logging.getLogger('api')


class PortfolioItemValidationMixin:
    def validate_quantity(self):
        if self.quantity <= 0:
            raise ValueError('quantity must be greater than zero')


@dataclasses.dataclass
class PortfolioSecurityAddSchema(PortfolioItemValidationMixin):
    ticker: str
    quantity: int


@dataclasses.dataclass
class PortfolioSecurityUpdateSchema(PortfolioItemValidationMixin):
    quantity: int


@dataclasses.dataclass
class PortfolioSecuritySchema(PortfolioItemValidationMixin):
    portfolio_id: int
    ticker: str
    quantity: int
    created_at: datetime.datetime


async def _serialize_portfolio_item(item: PortfolioItem) -> dict:
    converter = ModelToDictConverter(
        source=item,
        schema=PortfolioSecuritySchema,
        fields_map={
            'ticker': 'security__ticker',
        },
    )
    return await converter.convert()


@api_view(
    methods=['POST'],
    login_required=True,
    permissions=[IsPortfolioOwner(argument_name='portfolio_id')],
    request_schema=PortfolioSecurityAddSchema,
)
async def add_portfolio_security(request, portfolio_id: int):
    item_schema: PortfolioSecurityAddSchema = request.populated_schema

    security: Security = await aget_object_or_404_json(
        Security.objects.only(),
        ticker=item_schema.ticker,
    )
    try:
        portfolio_item: PortfolioItem = await PortfolioItem.objects.acreate(
            portfolio_id=portfolio_id,
            security=security,
        )
    except IntegrityError:
        logger.warning(
            'User attempted to add the same portfolio security twice',
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
    request,
    portfolio_id: int,
    security_ticker: int,
):
    portfolio_item: PortfolioItem = await aget_object_or_404_json(
        PortfolioItem.objects.select_related('security').only(
            'portfolio_id',
            'quantity',
            'created_at',
            'security__ticker',
        ),
        portfolio__id=portfolio_id,
        security__ticker=security_ticker,
        object_error_name='portfolio security',
    )
    schema: PortfolioSecurityUpdateSchema = request.populated_schema
    portfolio_item.quantity = schema.quantity
    await portfolio_item.asave(update_fields=['quantity'])

    return JsonResponse(await _serialize_portfolio_item(portfolio_item))


dispatcher = create_dispatcher(
    patch=update_portfolio_security,
)
