from django.db import models

from utils.abstract_models import CreatedUpdatedAbstractModel


class PortfolioItem(CreatedUpdatedAbstractModel, models.Model):
    portfolio = models.ForeignKey(
        to='Portfolio',
        related_name='items',
        related_query_name='item',
        on_delete=models.CASCADE,
    )
    security = models.ForeignKey(
        to='exchange.Security',
        related_name='portfolio_items',
        related_query_name='portfolio_item',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = (('portfolio', 'security'),)

    def __str__(self):
        return f'{self.portfolio} - {self.security}'
