"""Database connection."""
import os
import sqlite3

from app.configs.db import DB_NAME, DB_PATH, DB_PRAGMA_WAL, DB_TIMEOUT
from app.constants.general import LOG_LEVEL_ERROR, LOG_LEVEL_EXCEPTION
from qpylib import qpylib


class Connection:
    """Database Connection Handler."""

    conn = None  # type: ignore
    cursor = None  # type: ignore

    def __init__(self):
        """Initialize the Connection Object."""
        database_location = os.path.join(DB_PATH, DB_NAME)
        try:
            self.conn = sqlite3.connect(database_location, timeout=DB_TIMEOUT)
            self.conn.execute(DB_PRAGMA_WAL)
            self.cursor = self.conn.cursor()
        except Exception as error:
            qpylib.log(str(error), level=LOG_LEVEL_EXCEPTION)

    def is_connected(self):
        """Check if database connection is established or not.

        :return: True if conneciton established, else false
        :rtype: bool
        """
        return self.conn is not None

    def get_cursor(self):
        """Get cursor for the database connection.

        :return: Cursor for the database
        :rtype: object
        """
        return self.cursor

    def commit(self):
        """Commit the changes to the database."""
        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()

    def execute(self, query, fields=None):
        """Execute query on the sqllite database connected, over cursor.

        :param cursor: Database connection cursor to execute queries
        :type cursor: object
        :param query: Query to be executed over the database
        :type query: str
        :param fields: Field values to be inserted, defaults to None
        :type fields: tuple, optional
        """
        try:
            if not fields:
                # It's either create table query, delete query, update query or select query.
                self.cursor.execute(query)
            else:
                # It's insert query
                self.cursor.execute(query, fields)
        except Exception as error:
            qpylib.log(str(query), level=LOG_LEVEL_ERROR)
            qpylib.log(str(fields), level=LOG_LEVEL_ERROR)
            qpylib.log(str(error), level=LOG_LEVEL_EXCEPTION)

    def fetchall(self):
        """Fetch all the records from the cursor.

        :return: List of records
        :rtype: list
        """
        return self.cursor.fetchall()
