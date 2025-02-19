import datetime as dt
import json
import logging
from typing import override

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


class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self._last_record_hash = None
        self._last_returned_json = None
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        # RotatingFileHandler calls format twice
        # when used with maxBytes argument.
        # So for this case we can cache the last call
        # as a little optimization.
        record_hash = hash(record)
        if self._last_record_hash == record_hash:
            return self._last_returned_json

        message = self._prepare_log_dict(record)
        result = json.dumps(message, default=str)

        self._last_record_hash = record_hash
        self._last_returned_json = result

        return result

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict:
        always_fields = {
            'message': record.getMessage(),
            'timestamp': dt.datetime.fromtimestamp(
                record.created,
                tz=dt.timezone.utc,
            ).isoformat(),
        }

        if record.exc_text:
            always_fields['traceback'] = record.exc_text
        elif record.exc_info is not None:
            always_fields['traceback'] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields['stack_info'] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message
