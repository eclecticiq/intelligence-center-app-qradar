"""Converters ."""

import datetime

from app.configs.db import DB_TIMESTAMP_FORMAT
from app.constants.general import GLUE_COLON, GLUE_HYPHEN, TIME_MILLISECOND


def convert_string_to_epoch(time_str):
    """Convert date time string to epoch.

    :param time_str: Date time string
    :type time_str: str
    :return: Epoch value with resepect to date time string
    :rtype: int
    """
    epoch = datetime.datetime.strptime(time_str, DB_TIMESTAMP_FORMAT)
    return int(epoch.timestamp())


def convert_time_to_seconds(timestamp):
    """Convert Epoch Time from milliseconds to seconds.

    :param timestamp: Epoch time number
    :type timestamp: int
    :return: Converted time in seconds, if it was in milliseconds
    :rtype: int
    """
    now = int(datetime.datetime.now().timestamp())
    if now < timestamp:
        timestamp = int(timestamp / TIME_MILLISECOND)
    return timestamp


def get_formatted_date(days):
    """Get Formatted datetime.

    :param days: backfill_time
    :type response: int
    :return: formatted date
    :rtype: str
    """
    time = datetime.datetime.now() - datetime.timedelta(days=days)
    return datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%f")


def get_current_time():
    """Get Current datetime.

    :return: current datetime
    :rtype: str
    """
    time = datetime.datetime.utcnow()
    return datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%f")


def format_time_to_iso(time):
    """Format time to ISO Format.

    :return: time
    :rtype: str
    """
    return datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%f")


def convert_epoch_to_date(timestamp, status, include_seconds=False):
    """Convert epoch time to human readable date time string.

    :param timestamp: epoch time
    :type timestamp: int
    :param status: Status to check whether to repond with date or time
    :type status: bool
    :param include_seconds: Check to include seconds in the repsonse, defaults to False
    :type include_seconds: bool, optional
    :return: String containing date or time
    :rtype: str
    """
    timestamp = convert_time_to_seconds(timestamp)
    date = datetime.datetime.fromtimestamp(timestamp)

    response = []
    glue = ""
    if status:
        response = [str(date.year), str(date.month), str(date.day)]
        glue = GLUE_HYPHEN
    else:
        resp_list = [str(date.hour), str(date.minute)]
        if include_seconds:
            resp_list.append(str(date.second))

        response = resp_list
        glue = GLUE_COLON

    return glue.join(response)
