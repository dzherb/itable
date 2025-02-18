from django.db import models

from utils.abstract_models import CreatedUpdatedAbstractModel


class TableSnapshotItem(CreatedUpdatedAbstractModel, models.Model):
    snapshot = models.ForeignKey(
        to='TableSnapshot',
        related_name='items',
        related_query_name='item',
        on_delete=models.CASCADE,
    )
    template_item = models.ForeignKey(
        to='TableTemplateItem',
        related_name='snapshot_items',
        related_query_name='snapshot_item',
        on_delete=models.CASCADE,
    )