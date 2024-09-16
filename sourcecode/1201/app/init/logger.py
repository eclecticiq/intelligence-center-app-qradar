"""Initialize logger for the scheduler ."""

import logging
import os
from logging.handlers import RotatingFileHandler

from app.configs.logs import (
    SCHEDULER_LOG_BACKUP_COUNT,
    SCHEDULER_LOG_FILE_DIR,
    SCHEDULER_LOG_FILE_DIR_PARENT,
    SCHEDULER_LOG_FILENAME,
    SCHEDULER_LOG_FORMAT,
    SCHEDULER_LOG_MAX_BYTES,
)
from app.constants.scheduler import SCHEDULER_LOG


def init_logger():
    """Create logger for scheduler.

    :return: scheduler logger
    :rtype: logger object
    """
    # Create logger to be used by scheduler
    logger = logging.getLogger(SCHEDULER_LOG)

    # Set log level
    logger.setLevel(logging.WARNING)

    # Create file on rotation basis
    filename = "/opt/app-root/store/log/scheduler.log"

    handler = RotatingFileHandler(
        filename,
        maxBytes=SCHEDULER_LOG_MAX_BYTES,
        backupCount=SCHEDULER_LOG_BACKUP_COUNT,
    )

    # Set log formatter
    handler.setFormatter(logging.Formatter(SCHEDULER_LOG_FORMAT))

    # Add handler to the log
    logger.addHandler(handler)

    return logger
