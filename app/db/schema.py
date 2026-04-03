import sqlite3


def initialize_database(database_path: str) -> None:
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS utilizatori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            parola_hash TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS sarcini (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titlu TEXT NOT NULL,
            descriere TEXT,
            finalizata INTEGER NOT NULL DEFAULT 0 CHECK (finalizata IN (0, 1)),
            utilizator_id INTEGER NOT NULL,
            FOREIGN KEY (utilizator_id) REFERENCES utilizatori(id) ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_sarcini_user_finalizata ON sarcini(utilizator_id, finalizata)"
    )

    connection.commit()
    connection.close()
