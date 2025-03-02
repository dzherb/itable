import typing

from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)
from utils.db_helpers import aatomic

if typing.TYPE_CHECKING:
    from investment_tables.models import TableTemplate
    from portfolio.models import Portfolio


class TableSnapshotQuerySet(models.QuerySet['TableSnapshot']):
    def active(self) -> typing.Self:
        return self.filter(is_active=True)

    def owned_by(self, user: AbstractUser) -> typing.Self:
        return self.filter(portfolio__owner=user)


class TableSnapshot(CreatedUpdatedAbstractModel, models.Model):
    name = models.CharField(max_length=255, default='')
    portfolio = models.ForeignKey(
        to='portfolio.Portfolio',
        on_delete=models.CASCADE,
        related_name='table_snapshots',
        related_query_name='table_snapshot',
    )
    template = models.ForeignKey(
        to='investment_tables.TableTemplate',
        on_delete=models.CASCADE,
        related_name='snapshots',
        related_query_name='snapshot',
    )
    template_items = models.ManyToManyField(
        to='investment_tables.TableTemplateItem',
        through='investment_tables.TableSnapshotItem',
        related_name='snapshots',
        related_query_name='snapshot',
    )

    is_active = models.BooleanField(default=True)

    objects = TableSnapshotQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    @classmethod
    @aatomic
    async def from_template(
        cls,
        template: 'TableTemplate',
        portfolio: 'Portfolio',
        name: str | None = None,
    ) -> 'TableSnapshot':
        if name is None:
            name = template.name

        snapshot: TableSnapshot = await cls.objects.acreate(
            portfolio=portfolio,
            template=template,
            name=name,
        )

        items_to_add = []
        async for item in template.items.all():
            items_to_add.append(item)

        await snapshot.template_items.aadd(*items_to_add, through_defaults={})
        return snapshot
