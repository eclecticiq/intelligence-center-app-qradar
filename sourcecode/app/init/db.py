"""Init db."""
from app.constants.general import LOG_LEVEL_ERROR
from app.constants.messages import DB_CONNECTION_ERROR
from app.database.connection import Connection
from app.database.operations import get_create_table_query, get_create_table_query_keys
from qpylib import qpylib


def init_db():
    """Initialise database."""
    conn = Connection()
    status = False
    counter = 0
    if conn.is_connected():
        # Get Keys for each table to be created
        widget_list = get_create_table_query_keys()
        for widget in widget_list:
            # Get create table query for the widget/table
            query = get_create_table_query(widget)
            # Execute Create table query
            conn.execute(query)
            counter += 1
        status = True
    else:
        qpylib.log(DB_CONNECTION_ERROR, level=LOG_LEVEL_ERROR)

    if counter:
        # Commit the changes
        conn.commit()
    # Close connection
    conn.close()
    return counter, status
