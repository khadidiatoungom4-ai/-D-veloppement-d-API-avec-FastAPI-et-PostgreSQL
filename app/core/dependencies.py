
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.core.security import decoder_access_token


# Indique à FastAPI où se trouve la route de connexion
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# Récupérer l'utilisateur connecté à partir de son token
def obtenir_utilisateur_connecte(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Utilisateur:

    erreur_authentification = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'authentification.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    donnees = decoder_access_token(token)

    if donnees is None:
        raise erreur_authentification

    email = donnees.get("sub")

    if email is None:
        raise erreur_authentification

    requete = select(Utilisateur).where(
        Utilisateur.email == email
    )

    utilisateur = db.scalar(requete)

    # Vérifier que le compte existe et qu'il est actif
    if utilisateur is None or not utilisateur.actif:
        raise erreur_authentification

    return utilisateur


def exiger_admin(
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte)
) -> Utilisateur:

    if utilisateur.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs."
        )

    return utilisateur


def exiger_tailleur_ou_admin(
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte)
) -> Utilisateur:
    if utilisateur.role not in ["tailleur", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au tailleur ou à l'administrateur."
        )

    return utilisateur
