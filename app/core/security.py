from pwdlib import PasswordHash

# Initialisation de l'algorithme Argon2
password_hash = PasswordHash.recommended()


# Fonction pour sécuriser un mot de passe
def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return password_hash.hash(mot_de_passe)


# Fonction pour vérifier un mot de passe
def verifier_mot_de_passe(
    mot_de_passe: str,
    mot_de_passe_hash: str
) -> bool:
    return password_hash.verify(
        mot_de_passe,
        mot_de_passe_hash
    )

from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Initialisation de l'algorithme Argon2
password_hash = PasswordHash.recommended()


# Hacher un mot de passe
def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return password_hash.hash(mot_de_passe)


# Vérifier un mot de passe
def verifier_mot_de_passe(
    mot_de_passe: str,
    mot_de_passe_hash: str
) -> bool:
    return password_hash.verify(
        mot_de_passe,
        mot_de_passe_hash
    )


# Créer un token JWT
def creer_access_token(
    donnees: dict,
    duree_validite: timedelta | None = None
) -> str:

    donnees_a_encoder = donnees.copy()

    if duree_validite is None:
        duree_validite = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    date_expiration = datetime.now(timezone.utc) + duree_validite

    donnees_a_encoder.update({
        "exp": date_expiration
    })

    token = jwt.encode(
        donnees_a_encoder,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Vérifier et décoder un token JWT
def decoder_access_token(token: str) -> dict | None:

    try:
        donnees = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return donnees

    except InvalidTokenError:
        return None
