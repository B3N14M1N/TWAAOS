import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    database_path: str
    secret_key: str
    jwt_algorithm: str
    token_expiry_minutes: int


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Environment variable {name} is required.")
    return value


@lru_cache
def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env", override=False)
    return Settings(
        app_name="Gestionar de sarcini",
        app_version="4.0.0",
        database_path=os.getenv("DATABASE_PATH", str(base_dir / "sarcini.db")),
        secret_key=_required_env("SECRET_KEY"),
        jwt_algorithm=os.getenv("ALGORITHM", "HS256"),
        token_expiry_minutes=int(os.getenv("EXPIRARE_TOKEN_MINUTE", "30")),
    )
