import io
import json
import logging.config

from django.conf import settings
from django.test import TestCase

from logging_config import setup_logging
from logging_config.formatters import _LogDict, JSONFormatter


class JSONLoggingTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.stream = io.StringIO()
        logging.config.dictConfig(
            {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'json': {
                        '()': JSONFormatter,
                        'fields_to_add': {
                            'timestamp': 'timestamp',
                            'logger': 'name',
                            'module': 'module',
                            'function': 'funcName',
                            'line': 'lineno',
                            'thread_name': 'threadName',
                        },
                    },
                },
                'handlers': {
                    'console': {
                        'class': logging.StreamHandler,
                        'formatter': 'json',
                        'level': logging.INFO,
                        'stream': self.stream,
                    },
                },
                'loggers': {
                    'root': {
                        'level': logging.INFO,
                        'handlers': ['console'],
                    },
                },
            },
        )

        logging.disable(logging.NOTSET)

        self.logger = logging.getLogger('')

    def tearDown(self):
        super().tearDown()
        self.stream.close()
        setup_logging(settings.BASE_DIR)
        logging.disable(logging.CRITICAL)

    def test_json_log_fields(self):
        self.logger.error('test message')
        log = self._get_last_log_from_stream()

        expected_fields = (
            'level',
            'message',
            'timestamp',
            'logger',
            'module',
            'function',
            'line',
            'thread_name',
        )

        self.assertEqual(log['message'], 'test message')
        self.assertEqual(len(log.keys()), len(expected_fields))

        for field in log.keys():
            self.assertIn(field, expected_fields)

    def test_json_log_can_contain_exception_traceback(self):
        try:
            1 / 0  # noqa: B018
        except ZeroDivisionError:
            self.logger.error('1/0 exception', exc_info=True)

        log = self._get_last_log_from_stream()

        self.assertEqual(log['message'], '1/0 exception')
        self.assertIn('ZeroDivisionError', log['traceback'])

    def test_json_log_can_contain_extra_fields(self):
        self.logger.info('test message', extra={'a': 'b'})
        log = self._get_last_log_from_stream()
        self.assertEqual(log['a'], 'b')

    def test_can_write_multiple_json_logs(self):
        self.logger.info('test message 1')
        log = self._get_last_log_from_stream()
        self.assertEqual(log['message'], 'test message 1')

        self.logger.info('test message 2')
        log = self._get_last_log_from_stream()
        self.assertEqual(log['message'], 'test message 2')

        self.logger.info('test message 3')
        log = self._get_last_log_from_stream()
        self.assertEqual(log['message'], 'test message 3')

    def _get_last_log_from_stream(self) -> _LogDict:
        self.stream.seek(0)
        log = self.stream.readlines()[-1]
        return json.loads(log)
