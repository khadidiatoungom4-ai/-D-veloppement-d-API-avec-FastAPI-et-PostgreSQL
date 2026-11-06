
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur
from app.core.security import (
    verifier_mot_de_passe,
    creer_access_token
)
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


def authentifier_utilisateur(
    db: Session,
    email: str,
    mot_de_passe: str
) -> dict:

    # Rechercher l'utilisateur par son email
    requete = select(Utilisateur).where(
        Utilisateur.email == email
    )

    utilisateur = db.scalar(requete)

    # Vérifier les identifiants et l'état du compte
    if (
        utilisateur is None
        or not verifier_mot_de_passe(
            mot_de_passe,
            utilisateur.mot_de_passe_hash
        )
        or not utilisateur.actif
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Créer le token JWT
    token = creer_access_token(
        donnees={"sub": utilisateur.email}
    )

    # Retourner les informations de connexion
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
