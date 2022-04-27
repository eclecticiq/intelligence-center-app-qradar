"""DB Utils."""

from app.utils.converters import convert_string_to_epoch, convert_time_to_seconds


def convert_time_field(field_value):
    """Convert provided value to valid unix epoch timestamp in seconds.

    :param field_value: Field value
    :type field_value: str / int
    :return: Converted timestamp in seconds
    :rtype: int
    """
    function = (
        convert_string_to_epoch
        if isinstance(field_value, str)
        else convert_time_to_seconds
    )
    return function(field_value)
