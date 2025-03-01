import abc
import asyncio
from collections.abc import Iterable, Mapping, Sequence
import dataclasses
import typing
from typing import override

from dacite.types import is_instance
from django.db import models

if typing.TYPE_CHECKING:
    from _typeshed import DataclassInstance


class Converter[T: models.Model, D: 'DataclassInstance', E](abc.ABC):
    def __init__(
        self,
        schema: type[D],
        source: T | models.QuerySet[T] | None = None,
        *,
        fields_map: Mapping[str, typing.Union[str, 'Converter']] | None = None,
        skip_fields: Iterable[str] | None = None,
        many: bool = False,
    ):
        self._source = source
        self._dataclass = schema

        if fields_map is None:
            fields_map = {}

        self._fields_map = fields_map

        if skip_fields is None:
            skip_fields = ()

        self._skip_fields: typing.Iterable[str] = set(skip_fields)
        self._many = many

    @abc.abstractmethod
    async def convert(self) -> E | Sequence[E]: ...

    def _set_source_if_empty(self, source: T | models.QuerySet[T]):
        if self._source is None:
            self._source = source


class ModelToDataclassConverter[T: models.Model, E: 'DataclassInstance'](
    Converter[T, E, E],
):
    @override
    async def convert(self) -> E | Sequence[E]:
        if self._source is None:
            raise AttributeError(
                'Failed to automatically resole the source field, '
                'you must explicitly set it on initialization',
            )

        if self._many:
            assert isinstance(self._source, models.QuerySet)
            tasks = []
            result = []
            async for item in self._source:
                tasks.append(asyncio.create_task(self._convert_one(item)))

            for task in await asyncio.gather(*tasks):
                result.append(task)

            return result

        return await self._convert_one(self._source)

    async def _convert_one(self, source: T | models.QuerySet[T]):
        fields = self._dataclass.__dataclass_fields__
        init_kwargs: dict[str, typing.Any] = {}
        for field_name in fields:
            if field_name in self._skip_fields:
                init_kwargs[field_name] = None
                continue

            lookup = self._fields_map.get(field_name) or field_name
            if isinstance(lookup, Converter):
                lookup._set_source_if_empty(source)
                init_kwargs[field_name] = await lookup.convert()
                continue

            instance_field_name: str = lookup

            # Handle complex field lookups like portfolio__owner__first_name
            instance_field_parts = instance_field_name.split('__')
            instance = source
            try:
                for part in instance_field_parts:
                    value = getattr(instance, part)
                    instance = value

            except AttributeError as e:
                raise AttributeError(
                    f'Model instance has no "{instance_field_name}" field',
                ) from e

            self._check_type(field_name, value)
            init_kwargs[field_name] = value

        return self._dataclass(**init_kwargs)

    def _check_type(self, field_name: str, value: typing.Any):
        # Dataclasses don't do type checking, so we check ourselves.
        field_type = self._dataclass.__annotations__[field_name]
        if not is_instance(value, field_type):
            raise TypeError(f'Type mismatch for field "{field_name}"')


type _SerializedDataclass = dict[str, typing.Any]


class ModelToDictConverter[T: models.Model, D: 'DataclassInstance'](
    Converter[T, D, _SerializedDataclass],
):
    def __init__(
        self,
        schema: type[D],
        source: T | models.QuerySet[T] | None = None,
        *,
        fields_map: Mapping[str, typing.Union[str, 'Converter']] | None = None,
        skip_fields: typing.Sequence[str] | None = None,
        many: bool = False,
    ):
        super().__init__(
            schema,
            source,
            fields_map=fields_map,
            skip_fields=skip_fields,
            many=many,
        )
        self._intermediate_converter = ModelToDataclassConverter[T, D](
            schema,
            source,
            fields_map=fields_map,
            skip_fields=skip_fields,
            many=many,
        )

    @override
    async def convert(
        self,
    ) -> _SerializedDataclass | Sequence[_SerializedDataclass]:
        result = await self._intermediate_converter.convert()

        if isinstance(result, Sequence) and self._many:
            return [self._dataclass_to_dict(item) for item in result]

        assert not isinstance(result, Sequence)
        return self._dataclass_to_dict(result)

    @staticmethod
    def _dataclass_to_dict(dataclass: D) -> _SerializedDataclass:
        return dataclasses.asdict(dataclass)
