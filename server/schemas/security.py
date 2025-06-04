from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class PortfolioSecurityBase(BaseModel):
    quantity: Annotated[int, Field(gt=0)]


class PortfolioSecurityCreateSchema(PortfolioSecurityBase):
    ticker: str


class PortfolioSecurityUpdateSchema(PortfolioSecurityBase):
    pass


class PortfolioSecuritySchema(PortfolioSecurityBase):
    portfolio_id: int
    ticker: str
    created_at: datetime
