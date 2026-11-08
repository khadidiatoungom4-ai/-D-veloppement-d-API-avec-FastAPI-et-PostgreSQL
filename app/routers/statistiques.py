from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import exiger_admin

from app.services.statistique_service import (
    obtenir_tableau_de_bord,
    obtenir_chiffre_affaires,
    obtenir_statistiques_types_vetement,
    obtenir_top_clients,
    obtenir_commandes_impayees,
)

from app.schemas.statistique import (
    TableauBordRead,
    ChiffreAffairesStatistiqueResponse,
    TypesVetementStatistiqueResponse,
    TopClientsStatistiqueResponse,
    CommandesImpayeesStatistiqueResponse,
)
router = APIRouter(
    prefix="/statistiques",
    tags=["Statistiques"],
)
@router.get(
    "/tableau-de-bord",
    response_model=TableauBordRead,
)
def lire_tableau_de_bord(
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_admin),
):
    return obtenir_tableau_de_bord(db)
@router.get(
    "/chiffre-affaires",
    response_model=ChiffreAffairesStatistiqueResponse,
)
def lire_chiffre_affaires(
    granularite: str = Query(default="jour", pattern="^(jour|mois)$"),
    date_debut: date | None = None,
    date_fin: date | None = None,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_admin),
):
    aujourd_hui = date.today()

    if date_debut is None:
        date_debut = aujourd_hui.replace(day=1)

    if date_fin is None:
        date_fin = aujourd_hui

    return obtenir_chiffre_affaires(
        db=db,
        granularite=granularite,
        date_debut=date_debut,
        date_fin=date_fin,
    )
@router.get(
    "/types-vetement",
    response_model=TypesVetementStatistiqueResponse,
)
def lire_statistiques_types_vetement(
    date_debut: date | None = None,
    date_fin: date | None = None,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_admin),
):
    aujourd_hui = date.today()

    if date_debut is None:
        date_debut = aujourd_hui.replace(day=1)

    if date_fin is None:
        date_fin = aujourd_hui

    return obtenir_statistiques_types_vetement(
        db=db,
        date_debut=date_debut,
        date_fin=date_fin,
    )
@router.get(
    "/top-clients",
    response_model=TopClientsStatistiqueResponse,
)
def lire_top_clients(
    date_debut: date | None = None,
    date_fin: date | None = None,
    limite: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_admin),
):
    aujourd_hui = date.today()

    if date_debut is None:
        date_debut = aujourd_hui.replace(day=1)

    if date_fin is None:
        date_fin = aujourd_hui

    return obtenir_top_clients(
        db=db,
        date_debut=date_debut,
        date_fin=date_fin,
        limite=limite,
    )
@router.get(
    "/impayes",
    response_model=CommandesImpayeesStatistiqueResponse,
)
def lire_commandes_impayees(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_admin),
):
    return obtenir_commandes_impayees(
        db=db,
        limit=limit,
        offset=offset,
    )