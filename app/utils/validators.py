"""Validators."""
import datetime

from app.configs.db import DB_TIMESTAMP_FORMAT


def is_valid_datetime(date):
    """Check if datetime provided is a valid datetime object or not.

    :param date: Datetime in string format
    :type date: str
    :return: True if its a valid datetime else false
    :rtype: bool
    """
    status = True
    if isinstance(date, str):
        try:
            datetime.datetime.strptime(date, DB_TIMESTAMP_FORMAT)
            status = True
        except (ValueError, Exception):
            status = False
    return status
