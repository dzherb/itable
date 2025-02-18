from django.conf import settings
from django.db import models

from utils.abstract_models import (
    CreatedUpdatedAbstractModel,
)


class TableSnapshot(CreatedUpdatedAbstractModel, models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    template = models.ForeignKey(to='TableTemplate', on_delete=models.CASCADE)

    def __str__(self):
        return self.template.name