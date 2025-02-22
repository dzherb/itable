import asyncio
import dataclasses
import typing
from typing import override, runtime_checkable

from dacite.types import is_instance
from django.db import models


@runtime_checkable
class Converter(typing.Protocol):
    async def convert(self) -> typing.Any: ...


class ModelToDataclassConverter(Converter):
    def __init__(
        self,
        source: models.Model | models.QuerySet,
        schema,
        *,
        fields_map: dict[str, str | Converter] | None = None,
        skip_fields: typing.Sequence[str] | None = None,
        many: bool = False,
    ):
        self._source = source
        self._dataclass = schema

        if fields_map is None:
            fields_map = {}

        self._fields_map = fields_map

        if skip_fields is None:
            skip_fields = ()
        self._skip_fields = set(skip_fields)

        self._many = many

    @override
    async def convert(self) -> typing.Any:
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

    async def _convert_one(self, source):
        fields = self._dataclass.__dataclass_fields__
        init_kwargs = {}
        for field_name in fields:
            if field_name in self._skip_fields:
                init_kwargs[field_name] = None
                continue

            lookup = self._fields_map.get(field_name) or field_name
            if isinstance(lookup, Converter):
                init_kwargs[field_name] = await lookup.convert()
                continue

            instance_field_name = lookup

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


class ModelToDictConverter(ModelToDataclassConverter):
    @override
    async def convert(self) -> typing.Any:
        result = await super().convert()

        if self._many:
            return list(map(dataclasses.asdict, result))

        return dataclasses.asdict(result)
