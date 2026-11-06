from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import (
    obtenir_utilisateur_connecte,
    exiger_accueil_ou_admin,
)

from app.models.utilisateur import Utilisateur

from app.schemas.commande import (
    CommandeCreate,
    CommandeUpdate,
    CommandeRead,
    CommandeListResponse,
    CommandeStatutUpdate
     )

from app.schemas.ligne_commande import LigneCommandeCreate

from app.services.commande_service import (
    creer_commande,
    lister_commandes,
    obtenir_commande_par_id,
    modifier_commande,
    ajouter_ligne_commande,
    supprimer_ligne_commande,
    changer_statut_commande,
    obtenir_historique_statuts,
)
from app.schemas.historique_statut import HistoriqueStatutRead
router = APIRouter(
    prefix="/api/v1/commandes",
    tags=["Commandes"],
)
@router.post(
    "",
    response_model=CommandeRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_une_commande(
    donnees: CommandeCreate,
    db: Session = Depends(get_db),
utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),):
    return creer_commande(
        db=db,
        donnees=donnees,
        utilisateur_id=utilisateur.id,
    )
@router.get(
    "",
    response_model=CommandeListResponse,
)
def obtenir_les_commandes(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    statut: str | None = Query(default=None),
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return lister_commandes(
        db=db,
        limit=limit,
        offset=offset,
        statut=statut,
    )
@router.get(
    "/{commande_id}",
    response_model=CommandeRead,
)
def obtenir_une_commande(
    commande_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return obtenir_commande_par_id(
        db=db,
        commande_id=commande_id,
    )
@router.patch(
    "/{commande_id}",
    response_model=CommandeRead,
)
def modifier_une_commande(
    commande_id: int,
    donnees: CommandeUpdate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),
):
    return modifier_commande(
        db=db,
        commande_id=commande_id,
        donnees=donnees,
    )
@router.post(
    "/{commande_id}/lignes",
    response_model=CommandeRead,
    status_code=status.HTTP_201_CREATED,
)
def ajouter_une_ligne(
    commande_id: int,
    donnees: LigneCommandeCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),
):
    return ajouter_ligne_commande(
        db=db,
        commande_id=commande_id,
        donnees=donnees,
    )
@router.delete(
    "/{commande_id}/lignes/{ligne_id}",
    response_model=CommandeRead,
)
def supprimer_une_ligne(
    commande_id: int,
    ligne_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),
):
    return supprimer_ligne_commande(
        db=db,
        commande_id=commande_id,
        ligne_id=ligne_id,
    )
@router.post(
    "/{commande_id}/statut",
    response_model=CommandeRead,
)
def changer_statut(
    commande_id: int,
    donnees: CommandeStatutUpdate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return changer_statut_commande(
        db=db,
        commande_id=commande_id,
        donnees=donnees,
        utilisateur_id=utilisateur.id,
        role=utilisateur.role,
    )
@router.get(
    "/{commande_id}/historique",
    response_model=list[HistoriqueStatutRead],
)
def consulter_historique_statuts(
    commande_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return obtenir_historique_statuts(
        db=db,
        commande_id=commande_id,
    )