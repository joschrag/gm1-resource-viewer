"""Setup module wide logging."""

import atexit
import logging
import logging.config
import logging.handlers
import pathlib
from typing import override

import yaml


def setup_logging():
    """Set logging options as detailed in log_config.yaml."""
    config_file = pathlib.Path.cwd() / "log_config.yaml"
    with open(config_file) as f_in:
        config = yaml.load(f_in, yaml.SafeLoader)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


class NonErrorFilter(logging.Filter):
    """Add custom filter class to filter non error logs."""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Add custom filter function to filter non error logs.

        Args:
            record (logging.LogRecord): log record

        Returns:
            bool: record log level is lower than errror, warning or critical
        """
        return record.levelno <= logging.INFO
