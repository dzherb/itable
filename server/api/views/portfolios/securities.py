from http import HTTPStatus
import logging

from django.http import HttpResponse, JsonResponse

from api.core.api_view import api_view
from api.permissions import IsPortfolioOwner
from api.typedefs import (
    AuthenticatedPopulatedSchemaRequest,
    AuthenticatedRequest,
)
from api.utils.dispatcher import create_dispatcher
from schemas.security import (
    PortfolioSecurityCreateSchema,
    PortfolioSecurityUpdateSchema,
)
from services.securities.service import (
    SecurityAlreadyExistsError,
    SecurityService,
)

logger = logging.getLogger('api')


@api_view(
    methods=['POST'],
    login_required=True,
    permissions=[IsPortfolioOwner(argument_name='portfolio_id')],
    request_schema=PortfolioSecurityCreateSchema,
)
async def add_portfolio_security(
    request: AuthenticatedPopulatedSchemaRequest[
        PortfolioSecurityCreateSchema
    ],
    portfolio_id: int,
) -> HttpResponse:
    try:
        portfolio_security = await SecurityService().add_portfolio_security(
            portfolio_id,
            request.populated_schema,
        )
    except SecurityAlreadyExistsError:
        logger.warning(
            'Client attempted to add the same portfolio security twice',
            extra={
                'user_id': request.user_id,
                'portfolio_id': portfolio_id,
                'ticker': request.populated_schema.ticker,
            },
        )

        return JsonResponse(
            {'error': 'security already exists'},
            status=HTTPStatus.BAD_REQUEST,
        )

    return JsonResponse(portfolio_security.model_dump())


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
    security_ticker: str,
) -> HttpResponse:
    portfolio_security = await SecurityService().update_portfolio_security(
        portfolio_id,
        request.populated_schema,
        security_ticker,
    )

    return JsonResponse(portfolio_security.model_dump())


@api_view(
    login_required=True,
    permissions=[IsPortfolioOwner(argument_name='portfolio_id')],
)
async def remove_portfolio_security(
    request: AuthenticatedRequest,
    portfolio_id: int,
    security_ticker: str,
) -> HttpResponse:
    await SecurityService().remove_portfolio_security(
        portfolio_id,
        security_ticker,
    )
    logger.info(
        'User deleted portfolio item',
        extra={
            'user_id': request.user_id,
            'portfolio_id': portfolio_id,
            'ticker': security_ticker,
        },
    )

    return JsonResponse({})


dispatcher = create_dispatcher(
    patch=update_portfolio_security,
    delete=remove_portfolio_security,
)
