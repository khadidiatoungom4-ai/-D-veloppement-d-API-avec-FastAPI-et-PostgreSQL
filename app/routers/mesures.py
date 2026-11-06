
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import (
    obtenir_utilisateur_connecte,
    exiger_tailleur_ou_admin
)

from app.schemas.mesure import MesureCreate, MesureRead, MesureUpdate
from app.services.mesure_service import (
    creer_mesure,
    obtenir_historique_mesures,
    obtenir_derniere_mesure,
    obtenir_mesure_par_id,
    modifier_mesure
    )


router = APIRouter(tags=["Mesures"])


# 1. Enregistrer une nouvelle prise de mesures
@router.post(
    "/clients/{client_id}/mesures",
    response_model=MesureRead,
    status_code=status.HTTP_201_CREATED
)
def route_creer_mesure(
    client_id: int,
    donnees: MesureCreate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_tailleur_ou_admin)
):
    return creer_mesure(
        db,
        client_id,
        donnees,
        utilisateur.id
    )


# 2. Consulter l'historique des mesures d'un client
@router.get(
    "/clients/{client_id}/mesures",
    response_model=list[MesureRead]
)
def route_historique_mesures(
    client_id: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(obtenir_utilisateur_connecte)
):
    return obtenir_historique_mesures(db, client_id)


# 3. Consulter la dernière prise de mesures
@router.get(
    "/clients/{client_id}/mesures/derniere",
    response_model=MesureRead
)
def route_derniere_mesure(
    client_id: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(obtenir_utilisateur_connecte)
):
    return obtenir_derniere_mesure(db, client_id)


# 4. Consulter une mesure par son identifiant
@router.get(
    "/mesures/{mesure_id}",
    response_model=MesureRead
)
def route_obtenir_mesure(
    mesure_id: int,
    db: Session = Depends(get_db),
    utilisateur=Depends(obtenir_utilisateur_connecte)
):
    return obtenir_mesure_par_id(db, mesure_id)


# 5. Modifier une prise de mesures
@router.patch(
    "/mesures/{mesure_id}",
    response_model=MesureRead
)
def route_modifier_mesure(
    mesure_id: int,
    donnees: MesureUpdate,
    db: Session = Depends(get_db),
    utilisateur=Depends(exiger_tailleur_ou_admin)
):
    return modifier_mesure(db, mesure_id, donnees)
