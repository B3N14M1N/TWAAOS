import sqlite3
from collections.abc import Generator


def get_db_connection(database_path: str) -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()
