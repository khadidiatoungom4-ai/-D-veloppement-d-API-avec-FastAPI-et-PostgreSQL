
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.client import ClientCreate, ClientRead, ClientListResponse
from app.services.client_service import creer_client, lister_clients


router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


# Route pour créer un client
@router.post("/", response_model=ClientRead, status_code=201)
def creer_un_client(
    donnees: ClientCreate,
    db: Session = Depends(get_db)
):
    return creer_client(db, donnees)


# Route pour consulter la liste des clients
@router.get("/", response_model=ClientListResponse)
def obtenir_clients(
    q: str | None = Query(default=None, min_length=2),
    genre: Literal["homme", "femme", "enfant"] | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    return lister_clients(
        db=db,
        q=q,
        genre=genre,
        limit=limit,
        offset=offset
    )
from app.services.client_service import (
    creer_client,
    lister_clients,
    obtenir_client,
    modifier_client
)
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientRead,
    ClientListResponse
)
# Route pour consulter la fiche d'un client
@router.get("/{client_id}", response_model=ClientRead)
def obtenir_fiche_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    return obtenir_client(db, client_id)
# Route pour modifier partiellement un client
@router.patch("/{client_id}", response_model=ClientRead)
def modifier_fiche_client(
    client_id: int,
    donnees: ClientUpdate,
    db: Session = Depends(get_db)
):
    return modifier_client(db, client_id, donnees)