from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)


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
        return self.template.name