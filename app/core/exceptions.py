class AppError(Exception):
    def __init__(self, message: str, status_code: int, error_code: str) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class AuthenticationError(AppError):
    def __init__(self, message: str = "Autentificare esuata.") -> None:
        super().__init__(message=message, status_code=401, error_code="AUTHENTICATION_ERROR")


class ConflictError(AppError):
    def __init__(self, message: str = "Resursa exista deja.") -> None:
        super().__init__(message=message, status_code=409, error_code="CONFLICT")


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Resursa nu a fost gasita.") -> None:
        super().__init__(message=message, status_code=404, error_code="RESOURCE_NOT_FOUND")


class PasswordPolicyError(AppError):
    def __init__(self, message: str = "Parola nu respecta politica de securitate.") -> None:
        super().__init__(message=message, status_code=422, error_code="PASSWORD_POLICY_ERROR")
