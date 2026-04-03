from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import get_auth_service
from schemas.auth import TokenRaspuns, UtilizatorInregistrare
from services.auth_service import AuthService

router = APIRouter(tags=["autentificare"])


@router.post("/inregistrare", status_code=status.HTTP_201_CREATED)
def inregistrare(
    utilizator: UtilizatorInregistrare,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    auth_service.register_user(utilizator.email, utilizator.parola)

    return {"mesaj": f"Utilizatorul {utilizator.email} a fost inregistrat cu succes."}


@router.post("/autentificare", response_model=TokenRaspuns)
def autentificare(
    formular: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenRaspuns:
    token = auth_service.authenticate(formular.username, formular.password)

    return TokenRaspuns(access_token=token)
