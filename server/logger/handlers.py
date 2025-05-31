import copy
import logging
import logging.handlers
from typing import override


class JSONAwareQueueHandler(logging.handlers.QueueHandler):
    """
    Queue handler that doesn't merge message and traceback.

    It gives more flexibility for underlying handlers
    and their formatters, especially JSONFormatter.
    """

    @override
    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        # Make copy of record to avoid affecting other handlers in the chain.
        record = copy.copy(record)

        message = record.getMessage()
        record.msg = message
        record.message = message

        if record.exc_info:
            record.exc_text = self._get_formatter().formatException(
                record.exc_info,
            )

        # Reset possibly unpickable attributes.
        record.args = None
        record.exc_info = None
        record.stack_info = None
        return record

    def _get_formatter(self) -> logging.Formatter:
        if self.formatter:
            return self.formatter
        return logging.Formatter()
