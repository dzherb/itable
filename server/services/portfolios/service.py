from api.utils import aget_object_or_404_json
from apps.portfolios.models import Portfolio
from schemas.portfolio import (
    PortfolioCreateSchema,
    PortfolioListSchema,
    PortfolioSchema,
    PortfolioSimpleSchema,
    PortfolioUpdateSchema,
)


class PortfolioService:
    async def get_portfolio(self, portfolio_id: int) -> PortfolioSchema:
        portfolio: Portfolio = await aget_object_or_404_json(
            Portfolio.objects.active().prefetch_securities(),
            pk=portfolio_id,
        )

        # todo error handling
        return PortfolioSchema.model_validate(portfolio, from_attributes=True)

    async def create_portfolio(
        self,
        portfolio_create: PortfolioCreateSchema,
        user_id: int,
    ) -> PortfolioSchema:
        portfolio: Portfolio = await Portfolio.objects.acreate(
            name=portfolio_create.name,
            owner_id=user_id,
        )

        return PortfolioSchema.model_validate(portfolio, from_attributes=True)

    async def update_portfolio(
        self,
        portfolio_id: int,
        portfolio_update: PortfolioUpdateSchema,
    ) -> PortfolioSchema:
        portfolio: Portfolio = await aget_object_or_404_json(
            Portfolio.objects.active().prefetch_securities(),
            pk=portfolio_id,
        )
        portfolio.name = portfolio_update.name
        await portfolio.asave(update_fields=['name'])

        return PortfolioSchema.model_validate(portfolio, from_attributes=True)

    async def delete_portfolio(self, portfolio_id: int) -> None:
        portfolio: Portfolio = await aget_object_or_404_json(
            Portfolio.objects.active().only(),
            pk=portfolio_id,
        )
        portfolio.is_active = False
        await portfolio.asave()

    async def get_user_portfolios(self, user_id: int) -> PortfolioListSchema:
        select_fields = tuple(PortfolioSimpleSchema.model_fields.keys())
        user_portfolios = Portfolio.objects.filter(
            owner_id=user_id,
        ).only(*select_fields)

        return PortfolioListSchema.model_validate(
            {'portfolios': [p async for p in user_portfolios]},
            from_attributes=True,
        )
