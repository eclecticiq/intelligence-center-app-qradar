"""Insert Queries."""

INSERT_TABLE_QUERIES = {
    "eiq_sighting": "INSERT INTO {table} (value, type, title, description, confidence, tags, time) VALUES(?, ?, ?, ?, ?, ?, ?)".format(
        table="eiq_sighting"
    ),
}
