"""This module initializes the database and contains the other submodules."""

import logging

from .setup_logging import NonErrorFilter, setup_logging  # noqa: F401

setup_logging()

logger = logging.getLogger(__name__)
