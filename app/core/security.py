from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt import InvalidTokenError

from core.config import Settings
from core.exceptions import AuthenticationError, PasswordPolicyError


_BCRYPT_MAX_PASSWORD_BYTES = 72


def _validate_password_bytes(password: str) -> None:
    if len(password.encode("utf-8")) > _BCRYPT_MAX_PASSWORD_BYTES:
        raise PasswordPolicyError("Parola este prea lunga. Limita este 72 bytes pentru bcrypt.")


def hash_password(password: str) -> str:
    _validate_password_bytes(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, settings: Settings) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.token_expiry_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError as exc:
        raise AuthenticationError("Token invalid sau expirat.") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise AuthenticationError("Token invalid sau expirat.")
    return subject
