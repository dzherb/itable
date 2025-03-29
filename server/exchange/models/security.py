import logging
import typing

from django.db import IntegrityError, models

from exchange.services.stock_markets import MOEX
from utils.abstract_models import CreatedUpdatedAbstractModel

logger = logging.getLogger('securities.models')


class Security(CreatedUpdatedAbstractModel, models.Model):
    ticker = models.CharField(max_length=5, unique=True, db_index=True)

    def __str__(self) -> str:
        return self.ticker

    @classmethod
    async def get_or_try_to_create_from_moex(cls, ticker: str) -> 'Security':
        """
        Tries to retrieve security from db.
        If it doesn't exist, tries to create it from MOEX.
        If both of the attempts falls, raises DoesNotExist.
        """
        try:
            return await cls.objects.aget(ticker=ticker)
        except cls.DoesNotExist as e:
            security = await cls.create_from_moex_if_exists(ticker)
            if security is None:
                raise e

            return security

    @classmethod
    async def create_from_moex_if_exists(
        cls,
        ticker: str,
    ) -> typing.Optional['Security']:
        result = list(await MOEX().get_securities(tickers=(ticker,)))
        if len(result) == 0:
            return None

        try:
            security = await cls.objects.acreate(ticker=ticker)
            logger.info(f'Security with ticker {ticker} is created from MOEX')
            return security
        except IntegrityError:
            return None
