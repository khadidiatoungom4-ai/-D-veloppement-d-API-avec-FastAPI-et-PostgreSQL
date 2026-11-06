
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurRead,
    UtilisateurUpdate,
    UtilisateurListResponse
)

from app.services.utilisateur_service import (
    creer_utilisateur,
    lister_utilisateurs,
    obtenir_utilisateur_par_id,
    modifier_utilisateur
)

from app.services.utilisateur_service import creer_utilisateur
from app.core.dependencies import exiger_admin


router = APIRouter(
    prefix="/api/v1/utilisateurs",
    tags=["Utilisateurs"]
)


@router.post(
    "/",
    response_model=UtilisateurRead,
    status_code=status.HTTP_201_CREATED
)
def creer_un_utilisateur(
    donnees: UtilisateurCreate,
    db: Session = Depends(get_db),
    administrateur: Utilisateur = Depends(exiger_admin)
):
    return creer_utilisateur(db, donnees)

@router.get("/", response_model=UtilisateurListResponse)
def consulter_utilisateurs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    administrateur: Utilisateur = Depends(exiger_admin)
):
    return lister_utilisateurs(
        db=db,
        limit=limit,
        offset=offset
    )

@router.get("/{utilisateur_id}", response_model=UtilisateurRead)
def consulter_un_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    administrateur: Utilisateur = Depends(exiger_admin)
):
    return obtenir_utilisateur_par_id(db, utilisateur_id)

@router.patch("/{utilisateur_id}", response_model=UtilisateurRead)
def modifier_un_utilisateur(
    utilisateur_id: int,
    donnees: UtilisateurUpdate,
    db: Session = Depends(get_db),
    administrateur: Utilisateur = Depends(exiger_admin)
):
    return modifier_utilisateur(
        db=db,
        utilisateur_id=utilisateur_id,
        donnees=donnees.model_dump(exclude_unset=True),
        administrateur=administrateur
    )