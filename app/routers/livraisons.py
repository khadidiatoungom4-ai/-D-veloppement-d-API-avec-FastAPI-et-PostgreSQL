from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    exiger_accueil_ou_admin,
    obtenir_utilisateur_connecte,
)
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.livraison import (
    LivraisonCreate,
    LivraisonRead,
    LivraisonConfirmation,
    LivraisonListeRead,

)
from app.services.livraison_service import (
    planifier_livraison,
    obtenir_livraison,
    confirmer_livraison,
    lister_livraisons
)

router = APIRouter(tags=["Livraisons"])


# Route 35 : planifier ou replanifier une livraison
@router.put(
    "/commandes/{commande_id}/livraison",
    response_model=LivraisonRead,
)
def programmer_livraison(
    commande_id: int,
    livraison_data: LivraisonCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),
):
    return planifier_livraison(
        db=db,
        commande_id=commande_id,
        donnees=livraison_data,
    )


# Route 36 : consulter la livraison d'une commande
@router.get(
    "/commandes/{commande_id}/livraison",
    response_model=LivraisonRead,
)
def consulter_livraison(
    commande_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return obtenir_livraison(
        db=db,
        commande_id=commande_id,
    )


# Route 37 : confirmer une livraison
@router.post(
    "/commandes/{commande_id}/livraison/confirmer",
    response_model=LivraisonRead,
)
def valider_livraison(
    commande_id: int,
    livraison_data: LivraisonConfirmation,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),
):
    return confirmer_livraison(
        db=db,
        commande_id=commande_id,
        donnees=livraison_data,
        utilisateur_id=utilisateur.id,
    )
# Route 38 : consulter toutes les livraisons
@router.get(
    "/livraisons",
    response_model=list[LivraisonListeRead],
)
def consulter_toutes_les_livraisons(
    statut: str | None = None,
    date_min: date | None = None,
    date_max: date | None = None,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return lister_livraisons(
        db=db,
     statut_livraison=statut,
        date_min=date_min,
        date_max=date_max,
    )