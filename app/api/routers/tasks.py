import sqlite3

from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_user, get_task_service
from schemas.task import SarcinaActualizare, SarcinaCreare, SarcinaRaspuns
from services.task_service import TaskService

router = APIRouter(prefix="/sarcini", tags=["sarcini"])


@router.get("", response_model=list[SarcinaRaspuns])
def obtine_sarcini(
    doar_nefinalizate: bool = False,
    utilizator_curent: sqlite3.Row = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> list[SarcinaRaspuns]:
    return [
        SarcinaRaspuns.model_validate(item)
        for item in task_service.list_tasks(utilizator_curent["id"], doar_nefinalizate)
    ]


@router.get("/{sarcina_id}", response_model=SarcinaRaspuns)
def obtine_sarcina(
    sarcina_id: int,
    utilizator_curent: sqlite3.Row = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> SarcinaRaspuns:
    sarcina = task_service.get_task(sarcina_id, utilizator_curent["id"])
    return SarcinaRaspuns.model_validate(sarcina)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SarcinaRaspuns)
def creeaza_sarcina(
    sarcina: SarcinaCreare,
    utilizator_curent: sqlite3.Row = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> SarcinaRaspuns:
    sarcina_noua = task_service.create_task(sarcina, utilizator_curent["id"])
    return SarcinaRaspuns.model_validate(sarcina_noua)


@router.put("/{sarcina_id}", response_model=SarcinaRaspuns)
def actualizeaza_sarcina(
    sarcina_id: int,
    date: SarcinaActualizare,
    utilizator_curent: sqlite3.Row = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> SarcinaRaspuns:
    sarcina = task_service.update_task(sarcina_id, date, utilizator_curent["id"])
    return SarcinaRaspuns.model_validate(sarcina)


@router.patch("/{sarcina_id}/finalizeaza", response_model=SarcinaRaspuns)
def finalizeaza_sarcina(
    sarcina_id: int,
    utilizator_curent: sqlite3.Row = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> SarcinaRaspuns:
    sarcina = task_service.finalize_task(sarcina_id, utilizator_curent["id"])
    return SarcinaRaspuns.model_validate(sarcina)


@router.delete("/{sarcina_id}")
def sterge_sarcina(
    sarcina_id: int,
    utilizator_curent: sqlite3.Row = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
) -> dict[str, str]:
    task_service.delete_task(sarcina_id, utilizator_curent["id"])

    return {"mesaj": f"Sarcina cu ID-ul {sarcina_id} a fost stearsa."}
