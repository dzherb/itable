import typing
from typing import final, override

from django.db import models

from apps import investment_tables
from apps.exchange.models import Security
from apps.exchange.services.synchronization.index_providers import (
    IndexProviderProtocol,
    SecurityWeightDict,
)
from apps.exchange.services.synchronization.index_providers.imoex import (
    IMOEXProvider,
)
from apps.exchange.services.synchronization.index_synchronizer_protocol import (  # noqa: E501
    IndexSynchronizerProtocol,
)
from apps.investment_tables.models import TableTemplate
from utils.db_helpers import aatomic


class SecurityWeightDictWithId(SecurityWeightDict):
    id: typing.NotRequired[int]


@final
class IMOEXSynchronizer(IndexSynchronizerProtocol):
    IMOEX_TABLE_TEMPLATE_SLUG = 'imoex'

    def __init__(self, *, provider: IndexProviderProtocol | None = None):
        self._provider = provider or IMOEXProvider()

    @override
    @aatomic
    async def synchronize(self) -> None:
        securities = await self._provider.get_index_content()

        ticker_to_security_map: dict[str, SecurityWeightDictWithId] = {
            security['ticker']: typing.cast(SecurityWeightDictWithId, security)
            for security in securities
        }
        tickers = list(ticker_to_security_map.keys())

        await Security.objects.abulk_create(
            [Security(ticker=ticker) for ticker in tickers],
            ignore_conflicts=True,
        )

        (
            table_template,
            _,
        ) = await TableTemplate.objects.aget_or_create(
            slug=self.IMOEX_TABLE_TEMPLATE_SLUG,
        )

        # This way we can get rid of securities that no longer
        # a part of the index. Later is_active is set to True
        # for currently active securities.
        await table_template.items.aupdate(is_active=False)

        db_securities: models.QuerySet[Security] = Security.objects.filter(
            ticker__in=tickers,
        )

        async for security in db_securities:
            ticker_to_security_map[security.ticker]['id'] = security.id

        template_items_to_create = []
        for security_dict in ticker_to_security_map.values():
            template_items_to_create.append(
                investment_tables.models.TableTemplateItem(
                    security_id=security_dict['id'],
                    template_id=table_template.id,
                    weight=security_dict['weight'],
                    is_active=True,
                ),
            )

        await investment_tables.models.TableTemplateItem.objects.abulk_create(
            template_items_to_create,
            update_conflicts=True,
            unique_fields=['security_id', 'template_id'],
            update_fields=['weight', 'is_active'],
        )
