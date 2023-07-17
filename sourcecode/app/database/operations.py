"""Database Operations."""

from app.queries.sqllite.create import CREATE_TABLE_QUERIES

from app.queries.sqllite.insert import INSERT_TABLE_QUERIES


def get_create_table_query(key):
    """Get Create table query by key.

    :param key: Widget name for which query to be searched
    :type key: str
    :return: Query string respective of widget name provided as a key, else None
    :rtype: str / None
    """
    return CREATE_TABLE_QUERIES.get(key, None)


def get_create_table_query_keys():
    """Get list of widget names present in CREATE_TABLE_QUERIES dictionary as a key for each query.

    :return: List of widget names for which create query is present
    :rtype: list
    """
    return CREATE_TABLE_QUERIES.keys()


def get_insert_table_query(name):
    """Get the insert table query for named widget.

    :param name: Widget name for which query is needed
    :type name: str
    :return: Query for the widget or None
    :rtype: str / None
    """
    return INSERT_TABLE_QUERIES.get(name, None)
