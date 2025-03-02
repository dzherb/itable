import typing

from django.conf import settings
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

from utils.abstract_models import CreatedUpdatedAbstractModel


class PortfolioQuerySet(models.QuerySet['Portfolio']):
    def active(self) -> typing.Self:
        return self.filter(is_active=True)

    def prefetch_items(self) -> typing.Self:
        from portfolio.models import PortfolioItem

        return self.prefetch_related(
            models.Prefetch(
                lookup='items',
                queryset=PortfolioItem.objects.select_related('security').only(
                    'security__ticker',
                    'quantity',
                ),
            ),
        )


class Portfolio(CreatedUpdatedAbstractModel, models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    securities = models.ManyToManyField(
        to='exchange.Security',
        through='portfolio.PortfolioItem',
        related_name='portfolios',
        related_query_name='portfolio',
    )

    is_active = models.BooleanField(default=True)

    objects = PortfolioQuerySet.as_manager()

    class Meta(TypedModelMeta):
        ordering = ('created_at',)

    def __str__(self) -> str:
        return self.name
