from dataclasses import is_dataclass
from http import HTTPStatus
import json
import typing
from typing import override

import dacite
from django.http import HttpRequest, HttpResponse, JsonResponse

from api.request_checkers.checker_protocol import Checker

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance


class _SchemaValidationRunner:
    """
    Runs schema "validate" methods if it has them.
    ValueError is expected to be raised on validation failure.
    """

    def __init__(self, populated_schema: 'DataclassInstance'):
        self._populated_schema = populated_schema

    def run_validations(self):
        for field in self._populated_schema.__dataclass_fields__.keys():
            self._validate_field(field)

        if hasattr(self._populated_schema, 'validate'):
            self._populated_schema.validate()

    def _validate_field[T](self, field: str) -> T:
        validation_method_name = 'validate_' + field
        if hasattr(self._populated_schema, validation_method_name):
            return getattr(self._populated_schema, validation_method_name)()

        value: T = getattr(self._populated_schema, field)
        return value


class SchemaChecker(Checker):
    def __init__(self, request_schema: type):
        if not (
            is_dataclass(request_schema) and isinstance(request_schema, type)
        ):
            raise TypeError('Expected a dataclass')

        self._request_schema = request_schema
        self._error: str | None = None

    @override
    async def check(self, request: HttpRequest, *args, **kwargs) -> bool:
        # Is request.body a blocking I/O operation?
        # Seems like currently there is no way to read it asynchronously.
        request_data = json.loads(request.body)
        try:
            populated_schema = dacite.from_dict(
                data_class=self._request_schema,
                data=request_data,
            )
            _SchemaValidationRunner(populated_schema).run_validations()
            request.populated_schema = populated_schema
            return True
        except dacite.WrongTypeError as e:
            self._error = str(e)
            return False
        except dacite.MissingValueError as e:
            self._error = str(e)
            return False
        except ValueError as e:
            self._error = str(e)
            return False

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': self._error},
            status=HTTPStatus.BAD_REQUEST,
        )
