from core.exceptions import ResourceNotFoundError
from db.repositories import TaskRepository
from schemas.task import SarcinaActualizare, SarcinaCreare


class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository

    def list_tasks(self, user_id: int, only_unfinished: bool) -> list[dict]:
        rows = self._task_repository.list_for_user(user_id, only_unfinished)
        return [self._map_task(row) for row in rows]

    def get_task(self, task_id: int, user_id: int) -> dict:
        row = self._task_repository.get_for_user(task_id, user_id)
        if row is None:
            raise ResourceNotFoundError("Sarcina nu a fost gasita.")
        return self._map_task(row)

    def create_task(self, task: SarcinaCreare, user_id: int) -> dict:
        row = self._task_repository.create_for_user(user_id, task)
        if row is None:
            raise ResourceNotFoundError("Sarcina nu a putut fi creata.")
        return self._map_task(row)

    def update_task(self, task_id: int, updates: SarcinaActualizare, user_id: int) -> dict:
        row = self._task_repository.update_for_user(task_id, user_id, updates)
        if row is None:
            raise ResourceNotFoundError("Sarcina nu a fost gasita.")
        return self._map_task(row)

    def finalize_task(self, task_id: int, user_id: int) -> dict:
        row = self._task_repository.finalize_for_user(task_id, user_id)
        if row is None:
            raise ResourceNotFoundError("Sarcina nu a fost gasita.")
        return self._map_task(row)

    def delete_task(self, task_id: int, user_id: int) -> None:
        _ = self.get_task(task_id, user_id)
        self._task_repository.delete_for_user(task_id, user_id)

    @staticmethod
    def _map_task(row) -> dict:
        data = dict(row)
        data["finalizata"] = bool(data["finalizata"])
        return data
