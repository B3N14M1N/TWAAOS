import sqlite3

from core.config import Settings
from core.exceptions import AuthenticationError, ConflictError
from core.security import create_access_token, decode_access_token, hash_password, verify_password
from db.repositories import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository, settings: Settings) -> None:
        self._user_repository = user_repository
        self._settings = settings

    def register_user(self, email: str, password: str) -> None:
        normalized_email = email.lower()
        if self._user_repository.get_by_email(normalized_email) is not None:
            raise ConflictError("Adresa de email este deja inregistrata.")

        try:
            self._user_repository.create(normalized_email, hash_password(password))
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Adresa de email este deja inregistrata.") from exc

    def authenticate(self, email: str, password: str) -> str:
        normalized_email = email.lower()
        user = self._user_repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user["parola_hash"]):
            raise AuthenticationError("Email sau parola incorecta.")

        return create_access_token(subject=user["email"], settings=self._settings)

    def get_current_user(self, token: str) -> sqlite3.Row:
        subject = decode_access_token(token, self._settings)
        user = self._user_repository.get_by_email(subject)
        if user is None:
            raise AuthenticationError("Token invalid sau expirat.")
        return user
