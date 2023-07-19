"""Database configurations."""
DB_PATH = "store"
DB_NAME = "eiq.db"
DB_TIMEOUT = 15.0
DB_PRAGMA_WAL = "PRAGMA journal_mode=WAL"


# Constants for db handler
DB_TIMESTAMP_FORMAT = "%b %d %Y %H:%M:%S"
DB_RANGE_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
AUDIT_TIMESTAMP_FORMAT = "%d %b %Y %H:%M:%S"
