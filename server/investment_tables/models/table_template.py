from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)


class TableTemplate(CreatedUpdatedAbstractModel, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
