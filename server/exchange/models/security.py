from django.db import models

from utils.abstract_models import CreatedUpdatedAbstractModel


class Security(CreatedUpdatedAbstractModel, models.Model):
    ticker = models.CharField(max_length=5, unique=True, db_index=True)

    def __str__(self) -> str:
        return self.ticker
