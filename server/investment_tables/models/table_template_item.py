from django.db import models

from utils.abstract_models import CreatedUpdatedAbstractModel


class TableTemplateItemQuerySet(models.QuerySet):
    def active(self):
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

    class Meta:
        unique_together = (('template', 'security'),)
        constraints = [
            models.CheckConstraint(
                name='weight_limit',
                check=models.Q(weight__gte=0, weight__lte=100),
            ),
        ]

    def __str__(self):
        return f'{self.template} - {self.security}'
