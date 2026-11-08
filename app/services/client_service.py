
import re

from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


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


def lister_clients(
    db: Session,
    q: str | None = None,
    genre: str | None = None,
    limit: int = 20,
    offset: int = 0
):
    # Construire les conditions de recherche
    conditions = []

    # Recherche dans le nom, le prénom et le téléphone
    if q:
        terme = f"%{q.strip()}%"

        conditions.append(
            or_(
                Client.nom.ilike(terme),
                Client.prenom.ilike(terme),
                Client.telephone.ilike(terme)
            )
        )

    # Filtrer par genre si le paramètre est renseigné
    if genre:
        conditions.append(Client.genre == genre)

    # Compter le nombre total de clients correspondant aux filtres
    requete_total = select(func.count()).select_from(Client)

    if conditions:
        requete_total = requete_total.where(*conditions)

    total = db.scalar(requete_total)

    # Récupérer les clients avec pagination
    requete = select(Client)

    if conditions:
        requete = requete.where(*conditions)

    requete = (
        requete
        .order_by(Client.nom, Client.prenom)
        .limit(limit)
        .offset(offset)
    )

    clients = db.scalars(requete).all()

    return {
        "items": clients,
        "total": total,
        "limit": limit,
        "offset": offset
    }
def obtenir_client(db: Session, client_id: int) -> Client:
    requete = select(Client).where(Client.id == client_id)

    client = db.scalar(requete)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client introuvable."
        )

    return client

def modifier_client(
    db: Session,
    client_id: int,
    donnees: ClientUpdate
) -> Client:
    client = obtenir_client(db, client_id)

    modifications = donnees.model_dump(exclude_unset=True)

    if "telephone" in modifications:
        telephone = normaliser_telephone(modifications["telephone"])

        requete = select(Client).where(
            Client.telephone == telephone,
            Client.id != client_id
        )

        client_existant = db.scalar(requete)

        if client_existant:
            raise HTTPException(
                status_code=409,
                detail="Ce numéro de téléphone est déjà enregistré."
            )

        modifications["telephone"] = telephone

    for champ, valeur in modifications.items():
        setattr(client, champ, valeur)

    db.commit()
    db.refresh(client)

    return client

def supprimer_client(db: Session, client_id: int) -> None:
    client = obtenir_client(db, client_id)

    if client.commandes:
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer un client ayant des commandes."
        )

    db.delete(client)
    db.commit()