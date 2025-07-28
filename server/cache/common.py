from datetime import datetime, timedelta
import json
from typing import cast, overload, Protocol

from pydantic import BaseModel, ValidationError

type _SupportedPrimitive = str | int | float
type _SupportedDict = dict[
    str,
    _SupportedPrimitive
    | _SupportedDict
    | list[_SupportedDict | _SupportedPrimitive],
]
type _SerializableValue = (
    BaseModel | _SupportedDict | list[_SupportedDict | _SupportedPrimitive]
)

type RawValue = bytes | _SupportedPrimitive
type Value = RawValue | _SerializableValue


class Cache(Protocol):
    @overload
    async def get(
        self,
        key: str,
    ) -> RawValue | None: ...

    @overload
    async def get[T: Value](
        self,
        key: str,
        *,
        as_type: type[T],
    ) -> T | None: ...

    @overload
    async def set(self, key: str, value: Value, *, ttl: timedelta) -> None: ...

    @overload
    async def set(
        self,
        key: str,
        value: Value,
        *,
        expires_at: datetime,
    ) -> None: ...

    @overload
    async def set(
        self,
        key: str,
        value: Value,
    ) -> None: ...

    async def delete(self, key: str) -> None: ...


class CacheError(Exception):
    pass


class ValueDeserializationError(CacheError):
    pass


class PickleMixin:
    def deserialize[T: Value](
        self,
        value: RawValue | None,
        as_type: type[T],
    ) -> T | None:
        if value is None:
            return None

        if isinstance(value, as_type):
            return value

        if issubclass(as_type, (dict, list, BaseModel)) and isinstance(
            value,
            (bytes, str),
        ):
            dict_data = json.loads(value)

            if issubclass(as_type, BaseModel):
                try:
                    return cast(T, as_type.model_validate(dict_data))
                except ValidationError as e:
                    raise ValueDeserializationError() from e

            return cast(T, dict_data)

        raise ValueDeserializationError(
            f"'Unsupported deserialization from type '{type(value)!r}' "
            f"to '{as_type!r}'",
        )

    def serialize(self, value: Value) -> RawValue:
        if isinstance(value, (bytes, str, int, float)):
            return value

        if isinstance(value, BaseModel):
            json_str = value.model_dump_json()
        else:
            json_str = json.dumps(value)

        return json_str.encode()
