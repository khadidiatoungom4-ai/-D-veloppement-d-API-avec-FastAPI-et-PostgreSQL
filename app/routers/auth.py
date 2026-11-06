
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import TokenResponse
from app.services.auth_service import authentifier_utilisateur


from app.core.dependencies import obtenir_utilisateur_connecte
from app.schemas.auth import UtilisateurConnecte

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentification"]
)


@router.post("/login", response_model=TokenResponse)
def login(
    formulaire: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return authentifier_utilisateur(
        db=db,
        email=formulaire.username,
        mot_de_passe=formulaire.password
    )

@router.get("/me", response_model=UtilisateurConnecte)
def obtenir_mon_profil(
    utilisateur=Depends(obtenir_utilisateur_connecte)
):
    return utilisateur
