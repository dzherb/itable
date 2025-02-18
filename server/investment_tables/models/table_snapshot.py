import typing

from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)
from utils.db_helpers import aatomic

if typing.TYPE_CHECKING:
    from investment_tables.models import TableTemplate
    from portfolio.models import Portfolio


class TableSnapshot(CreatedUpdatedAbstractModel, models.Model):
    portfolio = models.ForeignKey(
        to='portfolio.Portfolio',
        on_delete=models.CASCADE,
        related_name='table_snapshots',
        related_query_name='table_snapshot',
    )
    template = models.ForeignKey(
        to='TableTemplate',
        on_delete=models.CASCADE,
        related_name='snapshots',
        related_query_name='snapshot',
    )
    template_items = models.ManyToManyField(
        to='TableTemplateItem',
        through='TableSnapshotItem',
        related_name='snapshots',
        related_query_name='snapshot',
    )

    def __str__(self):
        return f'{self.template.name} - {self.portfolio}'

    @classmethod
    @aatomic
    async def from_template(
        cls,
        template: 'TableTemplate',
        portfolio: 'Portfolio',
    ) -> typing.Self:
        snapshot: TableSnapshot = await cls.objects.acreate(
            portfolio=portfolio,
            template=template,
        )

        items_to_add = []
        async for item in template.items.all():
            items_to_add.append(item)

        await snapshot.template_items.aadd(*items_to_add, through_defaults={})
        return snapshot
