from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)


class TableTemplate(CreatedUpdatedAbstractModel, models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=20, unique=True)
    securities = models.ManyToManyField(
        to='exchange.Security',
        through='investment_tables.TableTemplateItem',
        related_name='templates',
        related_query_name='template',
    )

    def __str__(self) -> str:
        return self.name
