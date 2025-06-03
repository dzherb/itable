import typing

from django.db import models
from django.http import Http404
from django.shortcuts import aget_object_or_404

from api import exceptions


async def aget_object_or_404_json[T: models.Model](
    source: type[T] | models.Manager[T] | models.QuerySet[T],
    *args: typing.Any,
    object_error_name: str | None = None,
    **kwargs: typing.Any,
) -> T:
    """
    Similar to Django aget_object_or_404 but returns JsonResponse instead.

    object_error_name can change json error message.
    For example, if entity_error_name=="delicious potato" then we got
    {"error": "delicious potato not found"}

    If object_error_name is None then we take the model's name.
    For example, if source==OrderItem then we got
    {"error": "order item not found"}
    """
    try:
        return await aget_object_or_404(source, *args, **kwargs)
    except Http404 as e:
        object_type: type[T] | str | None = None
        if object_error_name:
            object_type = object_error_name
        elif isinstance(source, (models.Manager, models.QuerySet)):
            object_type = source.model
        elif issubclass(source, models.Model):
            object_type = source

        raise exceptions.NotFoundError(object_type=object_type) from e
