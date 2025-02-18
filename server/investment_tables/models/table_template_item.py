from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from utils.abstract_models import CreatedUpdatedAbstractModel


class TableTemplateItem(CreatedUpdatedAbstractModel, models.Model):
    weight = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    template = models.ForeignKey(
        to="TableTemplate",
        related_name="items",
        related_query_name="item",
        on_delete=models.CASCADE,
    )
    security = models.ForeignKey(
        to='exchange.Security',
        related_name="template_items",
        related_query_name="template_item",
        on_delete=models.CASCADE,
    )