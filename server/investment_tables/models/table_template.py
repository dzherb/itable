from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)


class TableTemplate(CreatedUpdatedAbstractModel, models.Model):
    name = models.CharField(max_length=255)
    securities = models.ManyToManyField(
        to='exchange.Security',
        through='TableTemplateItem',
        related_name='templates',
        related_query_name='template',
    )

    def __str__(self):
        return self.name
