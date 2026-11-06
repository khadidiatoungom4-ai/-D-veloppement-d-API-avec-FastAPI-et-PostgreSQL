from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import obtenir_utilisateur_connecte, exiger_admin
from app.database import get_db
from app.schemas.type_vetement import (
    TypeVetementCreate,
    TypeVetementUpdate,
    TypeVetementRead,
)
from app.services.type_vetement_service import (
    creer_type_vetement,
    lister_types_vetement,
    obtenir_type_vetement,
    modifier_type_vetement,
)

router = APIRouter(
    prefix="/api/v1/catalogue",
    tags=["Catalogue"]
)


@router.post("/", response_model=TypeVetementRead, status_code=201)
def creer_prestation(
    donnees: TypeVetementCreate,
    db: Session = Depends(get_db),
    administrateur=Depends(exiger_admin),
):
    return creer_type_vetement(db, donnees)


@router.get("/", response_model=list[TypeVetementRead])
def obtenir_catalogue(
    db: Session = Depends(get_db),
    utilisateur_connecte=Depends(obtenir_utilisateur_connecte),
):
    return lister_types_vetement(db)


@router.get("/{type_vetement_id}", response_model=TypeVetementRead)
def obtenir_prestation(
    type_vetement_id: int,
    db: Session = Depends(get_db),
    utilisateur_connecte=Depends(obtenir_utilisateur_connecte),
):
    return obtenir_type_vetement(db, type_vetement_id)


@router.patch("/{type_vetement_id}", response_model=TypeVetementRead)
def modifier_prestation(
    type_vetement_id: int,
    donnees: TypeVetementUpdate,
    db: Session = Depends(get_db),
    administrateur=Depends(exiger_admin),
):
    return modifier_type_vetement(db, type_vetement_id, donnees)