from dataclasses import is_dataclass
from http import HTTPStatus
import inspect
import json
import typing
from typing import override

import dacite
from dacite.types import is_optional
from django.http import HttpRequest, HttpResponse, JsonResponse
from pydantic import BaseModel, ValidationError

from api.request_checkers.checker_protocol import Checker

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance


class PopulatedSchemaRequest[T: 'DataclassInstance' | BaseModel](HttpRequest):
    populated_schema: T


class SchemaValidationError(ValueError):
    def __init__(
        self,
        message: str,
        response_status: int = HTTPStatus.BAD_REQUEST,
    ) -> None:
        self.message = message
        self.response_status = response_status


class _SchemaValidationRunner:
    """
    Runs schema "validate" methods if it has them.
    ValueError is expected to be raised on validation failure.
    """

    def __init__(self, populated_schema: 'DataclassInstance'):
        self._populated_schema = populated_schema

    async def run_validators(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        for field in self._populated_schema.__dataclass_fields__:
            if self._should_validate(field):
                await self._validate_field(field)

        if not hasattr(self._populated_schema, 'validate'):
            return

        if inspect.iscoroutinefunction(self._populated_schema.validate):
            await self._populated_schema.validate(
                request,
                *args,
                **kwargs,
            )
            return

        self._populated_schema.validate(
            request,
            *args,
            **kwargs,
        )

    async def _validate_field(self, field: str) -> typing.Any:
        validation_method_name = 'validate_' + field
        if hasattr(self._populated_schema, validation_method_name):
            method = getattr(self._populated_schema, validation_method_name)

            if inspect.iscoroutinefunction(method):
                return await method()

            return method()

        value: typing.Any = getattr(self._populated_schema, field)

        return value

    def _should_validate(self, field: str) -> bool:
        field_type = self._populated_schema.__annotations__[field]
        field_value = getattr(self._populated_schema, field)

        return not (is_optional(field_type) and field_value is None)


class BaseSchemaChecker(Checker):
    def _get_request_data(self, request: HttpRequest) -> dict[str, typing.Any]:
        if request.method == 'GET':
            return dict(request.GET)

        # Is request.body a blocking I/O operation?
        # Seems like currently there is no way to read it asynchronously.
        try:
            result = json.loads(request.body)
            return typing.cast(dict[str, typing.Any], result)
        except json.JSONDecodeError as e:
            raise ValueError('request body contains invalid json') from e


class DataclassSchemaChecker[D: 'DataclassInstance'](BaseSchemaChecker):
    def __init__(self, request_schema: type[D]):
        if not (
            is_dataclass(request_schema) and isinstance(request_schema, type)
        ):
            raise TypeError('Expected a dataclass')

        self._request_schema = request_schema
        self._error: str | None = None
        self._response_status: int = HTTPStatus.BAD_REQUEST

    @override
    async def check(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> bool:
        try:
            request_data = self._get_request_data(request)
            populated_schema = dacite.from_dict(
                data_class=self._request_schema,
                data=request_data,
            )
            await _SchemaValidationRunner(
                populated_schema=populated_schema,
            ).run_validators(request, *args, **kwargs)

            request = typing.cast(PopulatedSchemaRequest[D], request)
            request.populated_schema = populated_schema
            return True
        except dacite.WrongTypeError as e:
            self._error = str(e)
            return False
        except dacite.MissingValueError as e:
            self._error = str(e)
            return False
        except SchemaValidationError as e:
            self._error = e.message
            self._response_status = e.response_status
            return False
        except ValueError as e:
            self._error = str(e)
            return False

    @override
    def on_failure_response(self) -> HttpResponse:
        return JsonResponse(
            data={'error': self._error},
            status=self._response_status,
        )


class PydanticSchemaChecker[B: BaseModel](BaseSchemaChecker):
    def __init__(self, request_schema: type[B]):
        if not issubclass(request_schema, BaseModel):
            raise TypeError('Expected a BaseModel subclass')

        self._request_schema = request_schema
        self._error: str | None = None
        self._response_status: int = HTTPStatus.BAD_REQUEST

    @override
    async def check(
        self,
        request: HttpRequest,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> bool:
        try:
            request_data = self._get_request_data(request)
        except ValueError as e:
            self._error = json.dumps({'error': str(e)})
            return False

        try:
            populated_schema = self._request_schema.model_validate(
                request_data,
            )
        except ValidationError as e:
            self._error = '{"error":' + e.json(include_url=False) + '}'
            return False

        request = typing.cast(PopulatedSchemaRequest[B], request)
        request.populated_schema = populated_schema
        return True

    @override
    def on_failure_response(self) -> HttpResponse:
        if self._error is None:
            return JsonResponse(
                {'error': 'unknown'},
                status=self._response_status,
            )

        return HttpResponse(
            content=self._error.encode(),
            content_type='application/json',
            status=self._response_status,
        )
