
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.client import ClientCreate, ClientRead
from app.services.client_service import creer_client


router = APIRouter(
    prefix="/api/v1/clients",
    tags=["Clients"]
)


@router.post("/", response_model=ClientRead, status_code=201)
def creer_un_client(
    donnees: ClientCreate,
    db: Session = Depends(get_db)
):
    return creer_client(db, donnees)
