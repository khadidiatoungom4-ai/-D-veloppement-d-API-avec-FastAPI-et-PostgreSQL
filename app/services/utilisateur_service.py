
from fastapi import HTTPException
from sqlalchemy import select, func

from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate
from app.core.security import hacher_mot_de_passe


def creer_utilisateur(
    db: Session,
    donnees: UtilisateurCreate
) -> Utilisateur:

    # Vérifier si l'email existe déjà
    requete = select(Utilisateur).where(
        Utilisateur.email == donnees.email
    )

    utilisateur_existant = db.scalar(requete)

    if utilisateur_existant:
        raise HTTPException(
            status_code=409,
            detail="Cette adresse email est déjà utilisée."
        )

    # Créer le nouvel utilisateur
    nouvel_utilisateur = Utilisateur(
        email=donnees.email,
        nom_complet=donnees.nom_complet,
        mot_de_passe_hash=hacher_mot_de_passe(
            donnees.mot_de_passe
        ),
        role=donnees.role,
        actif=True
    )

    # Enregistrer dans PostgreSQL
    db.add(nouvel_utilisateur)
    db.commit()
    db.refresh(nouvel_utilisateur)

    return nouvel_utilisateur

def lister_utilisateurs(
    db: Session,
    limit: int = 20,
    offset: int = 0
) -> dict:

    # Compter le nombre total d'utilisateurs
    requete_total = select(func.count()).select_from(Utilisateur)
    total = db.scalar(requete_total)

    # Récupérer les utilisateurs de la page demandée
    requete = (
        select(Utilisateur)
        .order_by(Utilisateur.nom_complet.asc())
        .limit(limit)
        .offset(offset)
    )

    utilisateurs = list(db.scalars(requete).all())

    return {
        "items": utilisateurs,
        "total": total,
        "limit": limit,
        "offset": offset
    }
def obtenir_utilisateur_par_id(db: Session, utilisateur_id: int) -> Utilisateur:
    requete = select(Utilisateur).where(Utilisateur.id == utilisateur_id)
    utilisateur = db.scalar(requete)

    if utilisateur is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable."
        )

    return utilisateur
def modifier_utilisateur(
    db: Session,
    utilisateur_id: int,
    donnees: dict,
    administrateur: Utilisateur
) -> Utilisateur:

    utilisateur = obtenir_utilisateur_par_id(db, utilisateur_id)

    # Vérification de la règle RG24
    if utilisateur_id == administrateur.id:

        if donnees.get("actif") is False:
            raise HTTPException(
                status_code=409,
                detail="Vous ne pouvez pas désactiver votre propre compte."
            )

        if donnees.get("role") not in (None, "admin") and "role" in donnees:
            raise HTTPException(
                status_code=409,
                detail="Vous ne pouvez pas retirer votre propre rôle administrateur."
            )

    # Modification des informations
    if donnees.get("nom_complet") is not None:
        utilisateur.nom_complet = donnees["nom_complet"]

    if donnees.get("role") is not None:
        utilisateur.role = donnees["role"]

    if donnees.get("actif") is not None:
        utilisateur.actif = donnees["actif"]

    if donnees.get("mot_de_passe") is not None:
        utilisateur.mot_de_passe_hash = hacher_mot_de_passe(
            donnees["mot_de_passe"]
        )

    db.commit()
    db.refresh(utilisateur)

    return utilisateur