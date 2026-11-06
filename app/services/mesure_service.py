
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.mesure import Mesure
from app.schemas.mesure import MesureCreate, MesureUpdate

def creer_mesure(
    db: Session,
    client_id: int,
    donnees: MesureCreate,
    utilisateur_id: int
) -> Mesure:

    # Vérifier que le client existe
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client introuvable."
        )

    # Récupérer les données fournies
    donnees_mesure = donnees.model_dump(exclude_none=True)

    # Associer la mesure au client et au tailleur connecté
    nouvelle_mesure = Mesure(
        **donnees_mesure,
        client_id=client_id,
        prise_par_id=utilisateur_id
    )

    db.add(nouvelle_mesure)
    db.commit()
    db.refresh(nouvelle_mesure)

    return nouvelle_mesure


def obtenir_historique_mesures(
    db: Session,
    client_id: int
) -> list[Mesure]:

    # Vérifier que le client existe
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client introuvable."
        )

    # Récupérer toutes les mesures, de la plus récente à la plus ancienne
    requete = (
        select(Mesure)
        .where(Mesure.client_id == client_id)
        .order_by(Mesure.date_prise.desc(), Mesure.id.desc())
    )

    return list(db.scalars(requete).all())


def obtenir_derniere_mesure(
    db: Session,
    client_id: int
) -> Mesure:

    # Vérifier que le client existe
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client introuvable."
        )

    # Récupérer la mesure la plus récente
    requete = (
        select(Mesure)
        .where(Mesure.client_id == client_id)
        .order_by(Mesure.date_prise.desc(), Mesure.id.desc())
        .limit(1)
    )

    mesure = db.scalars(requete).first()

    if mesure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune mesure enregistrée pour ce client."
        )

    return mesure


def obtenir_mesure_par_id(
    db: Session,
    mesure_id: int
) -> Mesure:

    mesure = db.get(Mesure, mesure_id)

    if mesure is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesure introuvable."
        )

    return mesure

def modifier_mesure(
    db: Session,
    mesure_id: int,
    donnees: MesureUpdate
) -> Mesure:

    # Rechercher la mesure
    mesure = obtenir_mesure_par_id(db, mesure_id)

    # Récupérer uniquement les champs envoyés
    modifications = donnees.model_dump(exclude_unset=True)

    champs_mesures = [
        "taille_cm",
        "tour_cou",
        "carrure_dos",
        "longueur_epaule",
        "tour_poitrine",
        "tour_taille",
        "tour_bassin",
        "longueur_manche",
        "tour_bras",
        "tour_poignet",
        "longueur_dos",
        "longueur_haut",
        "longueur_pantalon",
        "tour_cuisse",
        "tour_genou",
        "bas_pantalon",
        "entrejambe",
        "longueur_robe"
    ]

    # Vérifier les mesures après modification
    mesures_finales = {}

    for champ in champs_mesures:
        if champ in modifications:
            mesures_finales[champ] = modifications[champ]
        else:
            mesures_finales[champ] = getattr(mesure, champ)

    if all(valeur is None for valeur in mesures_finales.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Une prise de mesures doit contenir au moins une mesure."
        )

    # Appliquer les modifications
    for champ, valeur in modifications.items():
        setattr(mesure, champ, valeur)

    db.commit()
    db.refresh(mesure)

    return mesure
