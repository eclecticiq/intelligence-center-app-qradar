"""Database Handler."""
from app.constants.columns import COLUMN_TIME

from app.constants.db import (
    DB_OPERATION_SELECT,
)
from app.constants.general import EMPTY_STRING, LOG_LEVEL_DEBUG
from app.database.connection import Connection
from app.database.operations import get_insert_table_query
from app.database.utils import convert_time_field
from app.utils.validators import is_valid_datetime
from qpylib import qpylib


def _prepare_data_to_insert(item, field_list):
    """Prepare data to insert in the table with the values and fields.

    :param item: Data to be inserted
    :type item: dict
    :param field_list: List of fields to map to column in the table
    :type field_list: list
    :return: List of fields with values to insert in the table
    :rtype: list
    """
    data_field_list = []
    if COLUMN_TIME in item and not (
        item[COLUMN_TIME] and is_valid_datetime(item[COLUMN_TIME])
    ):
        # It's not a valid datetime value, no need to continue further.
        return data_field_list

    for field in field_list:
        field_value = EMPTY_STRING
        if field in item and item[field] is not None:
            if COLUMN_TIME == field:
                # It's a valid time field, convert it to unix epoch in seconds from either string or milliseconds
                field_value = convert_time_field(item[field])
            else:
                field_value = item[field]

        data_field_list.append(field_value)
    return data_field_list


def insert_data_to_table(results, widget, field_list):
    """Insert data to the widget table.

    :param results: Data to be inserted into the table
    :type results: list
    :param widget: Widget (table) for which data to be inserted
    :type widget: str
    :param field_list: List of table fields
    :type field_list: list
    """
    query = get_insert_table_query(widget)
    qpylib.log(str(query), level=LOG_LEVEL_DEBUG)
    count = 0
    conn = Connection()
    for item in results:
        qpylib.log(str(item), level=LOG_LEVEL_DEBUG)
        data_field_list = _prepare_data_to_insert(item, field_list)
        qpylib.log(str(data_field_list), level=LOG_LEVEL_DEBUG)
        # Execute insert query
        if len(data_field_list) > 0:
            field_tuple = tuple(data_field_list)
            qpylib.log(str(field_tuple), level=LOG_LEVEL_DEBUG)
            conn.execute(query, field_tuple)
            count += 1
    # Commit the inserted data
    if count:
        conn.commit()
    conn.close()


def query_operations(query, operation="select"):
    """Perform the operation mentioned in operation on the query.

    If it is a select query, return the result of the select else save changes as per update and delete query and commit.

    :param query: Query to be executed
    :type query: str
    :param operation: Operation to be performed, SELECT / UPDTAE / DELETE
    :type operation: str
    :return: Query result, if select query
    :rtype: list / None
    """
    conn = Connection()
    conn.execute(query)
    result = None
    if DB_OPERATION_SELECT == operation:
        # It's a select query
        result = conn.fetchall()
    else:
        # It is update or delete query. Commit the changes
        conn.commit()
    conn.close()
    return result
