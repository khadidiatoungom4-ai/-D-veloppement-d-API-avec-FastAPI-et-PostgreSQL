from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    exiger_admin,
    exiger_accueil_ou_admin,
    obtenir_utilisateur_connecte,
)
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.paiement import PaiementCreate, PaiementRead
from app.services.paiement_service import (
    enregistrer_paiement,
    lister_paiements,
    annuler_paiement,
)

router = APIRouter(tags=["Paiements"])


@router.post(
    "/commandes/{commande_id}/paiements",
    response_model=PaiementRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_paiement(
    commande_id: int,
    paiement_data: PaiementCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_accueil_ou_admin),
):
    return enregistrer_paiement(
        db=db,
        commande_id=commande_id,
        paiement_data=paiement_data,
        utilisateur_id=utilisateur.id,
    )


@router.get(
    "/commandes/{commande_id}/paiements",
    response_model=list[PaiementRead],
)
def consulter_paiements(
    commande_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_connecte),
):
    return lister_paiements(
        db=db,
        commande_id=commande_id,
    )


@router.delete(
    "/paiements/{paiement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def supprimer_paiement(
    paiement_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(exiger_admin),
):
    annuler_paiement(
        db=db,
        paiement_id=paiement_id,
    )