"""Create table Queries."""

CREATE_TABLE_QUERIES = {
    "eiq_sighting": """CREATE TABLE IF NOT EXISTS {table} (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            value TEXT,
                            type TEXT,
                            title TEXT,
                            description TEXT,
                            confidence TEXT,
                            tags TEXT,
                            time TIMESTAMP
                        )""".format(
        table="eiq_sighting"
    ),
}
