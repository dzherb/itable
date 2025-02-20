from typing import final, override

from exchange.exchange.synchronization.index_providers import (
    IndexProviderProtocol,
)
from exchange.exchange.synchronization.index_providers.imoex import (
    IMOEXProvider,
)
from exchange.exchange.synchronization.index_synchronizer_protocol import (
    IndexSynchronizerProtocol,
)
import exchange.models
import investment_tables.models
from utils.db_helpers import aatomic


@final
class IMOEXSynchronizer(IndexSynchronizerProtocol):
    IMOEX_TABLE_TEMPLATE_SLUG = 'imoex'

    def __init__(self, *, provider: IndexProviderProtocol | None = None):
        self._provider = provider or IMOEXProvider()

    @override
    @aatomic
    async def synchronize(self):
        securities = await self._provider.get_index_content()

        ticker_to_security_map: dict[str, dict[str, str]] = {
            security['ticker']: security for security in securities
        }
        tickers = list(ticker_to_security_map.keys())

        await exchange.models.Security.objects.abulk_create(
            [exchange.models.Security(ticker=ticker) for ticker in tickers],
            ignore_conflicts=True,
        )

        (
            table_template,
            _,
        ) = await (
            investment_tables.models.TableTemplate.objects.aget_or_create(
                slug=self.IMOEX_TABLE_TEMPLATE_SLUG,
            )
        )

        # This way we can get rid of securities that no longer
        # a part of the index. Later is_active is set to True
        # for currently active securities.
        await table_template.items.aupdate(is_active=False)

        async for security in exchange.models.Security.objects.filter(
            ticker__in=tickers,
        ):
            ticker_to_security_map[security.ticker]['id'] = security.id

        template_items_to_create = []
        for security in ticker_to_security_map.values():
            template_items_to_create.append(
                investment_tables.models.TableTemplateItem(
                    security_id=security['id'],
                    template_id=table_template.id,
                    weight=security['weight'],
                    is_active=True,
                ),
            )

        await investment_tables.models.TableTemplateItem.objects.abulk_create(
            template_items_to_create,
            update_conflicts=True,
            unique_fields=['security_id', 'template_id'],
            update_fields=['weight', 'is_active'],
        )
