from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientRead,
    ClientListResponse
)

from app.services.client_service import (
    creer_client,
    lister_clients,
    obtenir_client,
    modifier_client,
    supprimer_client,
)

from app.core.dependencies import exiger_admin, obtenir_utilisateur_connecte

router = APIRouter(
    prefix="/api/v1/clients",
    tags=["Clients"]
)


# Route pour créer un client
@router.post("/", response_model=ClientRead, status_code=201)
def creer_un_client(
    donnees: ClientCreate,
    db: Session = Depends(get_db),
    utilisateur_connecte=Depends(obtenir_utilisateur_connecte)
):
    return creer_client(db, donnees)


# Route pour consulter la liste des clients
@router.get("/", response_model=ClientListResponse)
def obtenir_clients(
    q: str | None = Query(default=None, min_length=2),
    genre: Literal["homme", "femme", "enfant"] | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    utilisateur_connecte=Depends(obtenir_utilisateur_connecte)
):
    return lister_clients(
        db=db,
        q=q,
        genre=genre,
        limit=limit,
        offset=offset
    )


# Route pour consulter la fiche d'un client
@router.get("/{client_id}", response_model=ClientRead)
def obtenir_fiche_client(
    client_id: int,
    db: Session = Depends(get_db),
    utilisateur_connecte=Depends(obtenir_utilisateur_connecte)
):
    return obtenir_client(db, client_id)


# Route pour modifier partiellement un client
@router.patch("/{client_id}", response_model=ClientRead)
def modifier_fiche_client(
    client_id: int,
    donnees: ClientUpdate,
    db: Session = Depends(get_db),
    utilisateur_connecte=Depends(obtenir_utilisateur_connecte)
):
    return modifier_client(db, client_id, donnees)
@router.delete("/{client_id}", status_code=204)
def supprimer_fiche_client(
    client_id: int,
    db: Session = Depends(get_db),
    administrateur=Depends(exiger_admin),
):
    supprimer_client(db, client_id)