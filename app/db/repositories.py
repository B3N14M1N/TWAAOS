import sqlite3

from schemas.task import SarcinaActualizare, SarcinaCreare


class UserRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_by_email(self, email: str) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT id, email, parola_hash FROM utilizatori WHERE email = ?",
            (email,),
        ).fetchone()

    def create(self, email: str, password_hash: str) -> None:
        self._connection.execute(
            "INSERT INTO utilizatori (email, parola_hash) VALUES (?, ?)",
            (email, password_hash),
        )
        self._connection.commit()


class TaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_for_user(self, user_id: int, only_unfinished: bool) -> list[sqlite3.Row]:
        if only_unfinished:
            return self._connection.execute(
                "SELECT id, titlu, descriere, finalizata, utilizator_id "
                "FROM sarcini WHERE utilizator_id = ? AND finalizata = 0 ORDER BY id DESC",
                (user_id,),
            ).fetchall()

        return self._connection.execute(
            "SELECT id, titlu, descriere, finalizata, utilizator_id "
            "FROM sarcini WHERE utilizator_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()

    def get_for_user(self, task_id: int, user_id: int) -> sqlite3.Row | None:
        return self._connection.execute(
            "SELECT id, titlu, descriere, finalizata, utilizator_id "
            "FROM sarcini WHERE id = ? AND utilizator_id = ?",
            (task_id, user_id),
        ).fetchone()

    def create_for_user(self, user_id: int, task: SarcinaCreare) -> sqlite3.Row | None:
        cursor = self._connection.execute(
            "INSERT INTO sarcini (titlu, descriere, utilizator_id) VALUES (?, ?, ?)",
            (task.titlu, task.descriere, user_id),
        )
        self._connection.commit()
        return self.get_for_user(cursor.lastrowid, user_id)

    def update_for_user(self, task_id: int, user_id: int, updates: SarcinaActualizare) -> sqlite3.Row | None:
        current = self.get_for_user(task_id, user_id)
        if current is None:
            return None

        current_data = dict(current)
        title = updates.titlu if updates.titlu is not None else current_data["titlu"]
        description = updates.descriere if updates.descriere is not None else current_data["descriere"]
        done = int(updates.finalizata) if updates.finalizata is not None else current_data["finalizata"]

        self._connection.execute(
            "UPDATE sarcini SET titlu = ?, descriere = ?, finalizata = ? WHERE id = ? AND utilizator_id = ?",
            (title, description, done, task_id, user_id),
        )
        self._connection.commit()
        return self.get_for_user(task_id, user_id)

    def finalize_for_user(self, task_id: int, user_id: int) -> sqlite3.Row | None:
        self._connection.execute(
            "UPDATE sarcini SET finalizata = 1 WHERE id = ? AND utilizator_id = ?",
            (task_id, user_id),
        )
        self._connection.commit()
        return self.get_for_user(task_id, user_id)

    def delete_for_user(self, task_id: int, user_id: int) -> None:
        self._connection.execute(
            "DELETE FROM sarcini WHERE id = ? AND utilizator_id = ?",
            (task_id, user_id),
        )
        self._connection.commit()
