from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Gestiune inventar", version="1.0.0")


class Produs(BaseModel):
    id: int
    nume: str
    pret: float
    stoc: int = 0


class InventarService:
    """Service simplu pentru operatii pe inventar in memorie."""

    def __init__(self) -> None:
        self._produse: list[Produs] = []

    def toate(self) -> list[Produs]:
        return self._produse

    def dupa_id(self, produs_id: int) -> Produs:
        for produs in self._produse:
            if produs.id == produs_id:
                return produs
        raise HTTPException(
            status_code=404,
            detail=f"Produsul cu ID-ul {produs_id} nu a fost gasit.",
        )

    def adauga(self, produs: Produs) -> Produs:
        self._produse.append(produs)
        return produs

    def sterge(self, produs_id: int) -> Produs:
        for index, produs in enumerate(self._produse):
            if produs.id == produs_id:
                return self._produse.pop(index)
        raise HTTPException(
            status_code=404,
            detail=f"Produsul cu ID-ul {produs_id} nu a fost gasit.",
        )


inventar_service = InventarService()


@app.get("/produse")
def obtine_toate_produsele() -> list[Produs]:
    # Returneaza toate produsele din inventar.
    return inventar_service.toate()


@app.get("/produse/{produs_id}")
def obtine_produs(produs_id: int) -> Produs:
    # Cauta produsul dupa id.
    return inventar_service.dupa_id(produs_id)


@app.post("/produse", status_code=201)
def adauga_produs(produs: Produs) -> Produs:
    # Adauga un produs nou in inventar.
    return inventar_service.adauga(produs)


@app.delete("/produse/{produs_id}")
def sterge_produs(produs_id: int) -> Produs:
    # Sterge produsul si il returneaza ca confirmare.
    return inventar_service.sterge(produs_id)
