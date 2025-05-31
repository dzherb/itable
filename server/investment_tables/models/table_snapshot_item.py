from collections.abc import Sequence
import typing

from django.core.exceptions import ValidationError
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

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
    coefficient = models.FloatField(default=1)

    class Meta(TypedModelMeta):
        unique_together: typing.ClassVar[Sequence[str]] = (
            ('snapshot', 'template_item'),
        )
        constraints: typing.ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                name='coefficient_is_not_negative',
                condition=models.Q(coefficient__gte=0),
            ),
        ]

    def __str__(self) -> str:
        return f'{self.snapshot} {self.template_item}'

    def clean(self) -> None:
        if self.snapshot.template_id != self.template_item.template_id:
            raise ValidationError('Inconsistent snapshot template')
