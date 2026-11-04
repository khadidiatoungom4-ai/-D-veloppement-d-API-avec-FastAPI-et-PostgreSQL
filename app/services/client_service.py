
import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate


def normaliser_telephone(telephone: str) -> str:
    # Supprimer les espaces, points, tirets et parenthèses
    telephone = re.sub(r"[\s.\-()]", "", telephone)

    # Vérifier le format : + facultatif, suivi de 6 à 20 chiffres
    if not re.fullmatch(r"\+?\d{6,20}", telephone):
        raise HTTPException(
            status_code=422,
            detail="Le numéro de téléphone doit contenir entre 6 et 20 chiffres."
        )

    return telephone


def creer_client(db: Session, donnees: ClientCreate) -> Client:
    # Normaliser le numéro
    telephone = normaliser_telephone(donnees.telephone)

    # Vérifier si le numéro existe déjà
    requete = select(Client).where(Client.telephone == telephone)
    client_existant = db.scalar(requete)

    if client_existant:
        raise HTTPException(
            status_code=409,
            detail="Ce numéro de téléphone est déjà enregistré."
        )

    # Préparer les données du nouveau client
    nouveau_client = Client(
        nom=donnees.nom,
        prenom=donnees.prenom,
        telephone=telephone,
        email=donnees.email,
        adresse=donnees.adresse,
        genre=donnees.genre,
        notes=donnees.notes
    )

    # Enregistrer dans PostgreSQL
    db.add(nouveau_client)
    db.commit()
    db.refresh(nouveau_client)

    return nouveau_client
