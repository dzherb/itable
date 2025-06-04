from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class PortfolioSecuritySchema(BaseModel):
    ticker: str
    quantity: int


class PortfolioSimpleSchema(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime


class PortfolioSchema(PortfolioSimpleSchema):
    securities: Annotated[
        list[PortfolioSecuritySchema],
        Field(alias='securities_prefetched', default_factory=list),
    ]


class PortfolioListSchema(BaseModel):
    portfolios: list[PortfolioSimpleSchema]


class PortfolioCreateSchema(BaseModel):
    # todo don't allow whitespaces
    name: Annotated[str, Field(min_length=1)]


class PortfolioUpdateSchema(PortfolioCreateSchema):
    pass
