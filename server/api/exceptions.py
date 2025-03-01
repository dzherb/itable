from functools import lru_cache

from django.db import models

from api.helpers.strings import undo_camel_case


class APIError(Exception):
    pass


class UnauthorizedError(APIError):
    pass


class NotFoundError(APIError):
    def __init__(self, object_type: type[models.Model] | str | None = None):
        base_message = 'not found'
        if object_type is None:
            self.message = base_message
            return

        entity_name = self._get_entity_friendly_name(object_type)
        self.message = f'{entity_name} {base_message}'

    @staticmethod
    @lru_cache(maxsize=20)
    def _get_entity_friendly_name(
        object_type: type[models.Model] | str,
    ) -> str:
        if not isinstance(object_type, str):
            object_type = undo_camel_case(object_type.__name__)

        return object_type.lower()
