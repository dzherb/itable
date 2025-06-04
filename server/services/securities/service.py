from django.db import IntegrityError

from api.exceptions import NotFoundError
from api.utils import aget_object_or_404_json
from apps.exchange.models import Security
from apps.portfolios.models import PortfolioItem
from schemas.security import (
    PortfolioSecurityCreateSchema,
    PortfolioSecuritySchema,
    PortfolioSecurityUpdateSchema,
)


class SecurityAlreadyExistsError(Exception):
    pass


class SecurityService:
    PORTFOLIO_ITEM_404_NAME = 'portfolio security'

    async def add_portfolio_security(
        self,
        portfolio_id: int,
        security_create: PortfolioSecurityCreateSchema,
    ) -> PortfolioSecuritySchema:
        try:
            security: Security = await Security.get_or_try_to_create_from_moex(
                ticker=security_create.ticker,
            )
        except Security.DoesNotExist as e:
            raise NotFoundError(Security) from e

        try:
            portfolio_item: PortfolioItem = (
                await PortfolioItem.objects.acreate(
                    portfolio_id=portfolio_id,
                    security=security,
                )
            )
        except IntegrityError as e:
            raise SecurityAlreadyExistsError() from e

        return PortfolioSecuritySchema(
            portfolio_id=portfolio_id,
            quantity=portfolio_item.quantity,
            ticker=security_create.ticker,
            created_at=portfolio_item.created_at,
        )

    async def update_portfolio_security(
        self,
        portfolio_id: int,
        portfolio_update: PortfolioSecurityUpdateSchema,
        security_ticker: str,
    ) -> PortfolioSecuritySchema:
        portfolio_item: PortfolioItem = await aget_object_or_404_json(
            PortfolioItem.objects.only(
                'portfolio_id',
                'quantity',
                'created_at',
            ),
            portfolio__id=portfolio_id,
            security__ticker=security_ticker,
            object_error_name=self.PORTFOLIO_ITEM_404_NAME,
        )
        portfolio_item.quantity = portfolio_update.quantity

        await portfolio_item.asave(update_fields=['quantity'])

        return PortfolioSecuritySchema(
            portfolio_id=portfolio_id,
            quantity=portfolio_item.quantity,
            ticker=security_ticker,
            created_at=portfolio_item.created_at,
        )

    async def remove_portfolio_security(
        self,
        portfolio_id: int,
        security_ticker: str,
    ) -> None:
        portfolio_item: PortfolioItem = await aget_object_or_404_json(
            PortfolioItem.objects.only(),
            portfolio_id=portfolio_id,
            security__ticker=security_ticker,
            object_error_name=self.PORTFOLIO_ITEM_404_NAME,
        )

        await portfolio_item.adelete()
