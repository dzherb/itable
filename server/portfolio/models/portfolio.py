from django.conf import settings
from django.db import models

from utils.abstract_models import CreatedUpdatedAbstractModel


class Portfolio(CreatedUpdatedAbstractModel, models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    securities = models.ManyToManyField(
        to='exchange.Security',
        through='PortfolioItem',
        related_name='portfolios',
        related_query_name='portfolio',
    )

    def __str__(self):
        return self.name
