from collections.abc import Sequence
import typing

from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

from utils.abstract_models import CreatedUpdatedAbstractModel


class TableTemplateItemQuerySet(models.QuerySet['TableTemplateItem']):
    def active(self) -> typing.Self:
        return self.filter(is_active=True)


class TableTemplateItem(CreatedUpdatedAbstractModel, models.Model):
    template = models.ForeignKey(
        to='TableTemplate',
        related_name='items',
        related_query_name='item',
        on_delete=models.CASCADE,
    )
    security = models.ForeignKey(
        to='exchange.Security',
        related_name='template_items',
        related_query_name='template_item',
        on_delete=models.CASCADE,
    )

    weight = models.FloatField(help_text='in %')
    is_active = models.BooleanField(default=True)

    objects = TableTemplateItemQuerySet.as_manager()

    class Meta(TypedModelMeta):
        unique_together: typing.ClassVar[Sequence[str]] = (
            ('template', 'security'),
        )
        constraints: typing.ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                name='weight_limit',
                condition=models.Q(weight__gte=0, weight__lte=100),
            ),
        ]

    def __str__(self) -> str:
        return f'{self.template} - {self.security}'
