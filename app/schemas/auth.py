from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UtilizatorInregistrare(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    parola: str = Field(min_length=8, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()

    @field_validator("parola")
    @classmethod
    def validate_password_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Parola este prea lunga. Limita este 72 bytes.")
        return value


class TokenRaspuns(BaseModel):
    access_token: str
    token_type: str = "bearer"
