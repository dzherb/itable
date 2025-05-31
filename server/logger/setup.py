import atexit
import json
import logging.config
import logging.handlers
from pathlib import Path


def setup(base_dir: Path) -> None:
    config_file = base_dir / 'logger' / 'config.json'
    with open(config_file) as f_in:
        config = json.load(f_in)

    # This way we don't get errors while starting django shell.
    # Seems like it struggles to resolve the path without base_dir.
    config['handlers']['file_json']['filename'] = (
        base_dir / config['handlers']['file_json']['filename']
    )

    logging.config.dictConfig(config)

    queue_handler = logging.getHandlerByName('queue_handler')
    if (
        queue_handler is not None
        and isinstance(queue_handler, logging.handlers.QueueHandler)
        and queue_handler.listener is not None
    ):
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
