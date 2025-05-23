from collections.abc import Callable
import dataclasses
import datetime
import functools
import json
import logging
import typing
from typing import final, override

from django.utils import timezone

LOG_RECORD_BUILTIN_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
    'taskName',
}

_LogDict = dict[str, str | int | float | None]


def _avoid_unnecessary_format_calls[T: logging.Formatter](
    fn: Callable[[T, logging.LogRecord], str],
) -> Callable[[T, logging.LogRecord], str]:
    # RotatingFileHandler calls format twice
    # when used with maxBytes argument.
    # So for this case we can cache the last call
    # as a little optimization.

    @dataclasses.dataclass
    class Cache:
        last_record_hash: int | None = None
        last_returned_message: str | None = None

    cache = Cache()

    @functools.wraps(fn)
    def wrapper(self: T, record: logging.LogRecord) -> str:
        record_hash = hash(record) + hash(record.created)
        if cache.last_record_hash == record_hash:
            return typing.cast(str, cache.last_returned_message)

        message = fn(self, record)

        cache.last_record_hash = record_hash
        cache.last_returned_message = message

        return cache.last_returned_message

    return wrapper


class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fields_to_add: dict[str, str] | None = None,
        sort_keys: bool = False,
    ):
        super().__init__()
        if fields_to_add is None:
            fields_to_add = {}

        self._fields_to_add = fields_to_add
        self._sort_keys = sort_keys

    @override
    @_avoid_unnecessary_format_calls
    def format(self, record: logging.LogRecord) -> str:
        log_dict = _LogDictBuilder(
            record=record,
            formatter=self,
            fields_to_add=self._fields_to_add,
        ).build()

        return json.dumps(log_dict, default=str, sort_keys=self._sort_keys)


@final
class _LogDictBuilder:
    def __init__(
        self,
        record: logging.LogRecord,
        fields_to_add: dict[str, str],
        formatter: logging.Formatter,
    ):
        self._record = record
        self._fields_to_add = fields_to_add
        self._formatter = formatter
        self._log_dict: _LogDict = {}

    def build(self) -> _LogDict:
        self._add_always_fields()
        self._add_user_configured_fields()
        self._add_traceback_and_stack_info()
        self._add_extra_fields()
        return self._log_dict

    def _add_always_fields(self) -> None:
        self._log_dict['level'] = self._record.levelname
        self._log_dict['message'] = self._record.getMessage()
        self._log_dict['timestamp'] = self._get_created_time()

    def _get_created_time(self) -> str:
        dt = datetime.datetime.fromtimestamp(self._record.created)
        return timezone.make_aware(dt).isoformat()

    def _add_user_configured_fields(self) -> None:
        for json_field, log_attribute in self._fields_to_add.items():
            if json_field not in self._log_dict and hasattr(
                self._record,
                log_attribute,
            ):
                self._log_dict[json_field] = getattr(
                    self._record,
                    log_attribute,
                )

    def _add_traceback_and_stack_info(self) -> None:
        if self._record.exc_text:
            self._log_dict['traceback'] = self._record.exc_text
        elif self._record.exc_info is not None:
            self._log_dict['traceback'] = self._formatter.formatException(
                self._record.exc_info,
            )

        if self._record.stack_info is not None:
            self._log_dict['stack_info'] = self._formatter.formatStack(
                self._record.stack_info,
            )

    def _add_extra_fields(self) -> None:
        for key, val in self._record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                self._log_dict[key] = val
