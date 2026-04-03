from pydantic import BaseModel, ConfigDict, Field


class SarcinaCreare(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titlu: str = Field(min_length=1, max_length=200)
    descriere: str | None = Field(default=None, max_length=1000)


class SarcinaActualizare(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titlu: str | None = Field(default=None, min_length=1, max_length=200)
    descriere: str | None = Field(default=None, max_length=1000)
    finalizata: bool | None = None


class SarcinaRaspuns(BaseModel):
    id: int
    titlu: str
    descriere: str | None
    finalizata: bool
    utilizator_id: int
