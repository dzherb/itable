from django.db import models
from django.db.models import Manager, QuerySet
from django.http import Http404
from django.shortcuts import aget_object_or_404

from api import exceptions


async def aget_object_or_404_json[T: models.Model](
    model: type[T] | Manager[T] | QuerySet[T],
    *args,
    **kwargs,
) -> T:
    """
    Similar to Django aget_object_or_404
    but returns JsonResponse instead.
    """
    try:
        return await aget_object_or_404(model, *args, **kwargs)
    except Http404 as e:
        raise exceptions.NotFoundError from e
