
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ligne_commande import (
    LigneCommandeCreate,
    LigneCommandeRead,
)

from app.schemas.historique_statut import HistoriqueStatutRead
class CommandeCreate(BaseModel):
    client_id: int
    mesure_id: int | None = None
    lignes: list[LigneCommandeCreate] = Field(min_length=1)
    remise: int = Field(default=0, ge=0)
    date_livraison_prevue: date | None = None
    notes: str | None = None


class CommandeUpdate(BaseModel):
    mesure_id: int | None = None
    date_livraison_prevue: date | None = None
    remise: int | None = Field(default=None, ge=0)
    notes: str | None = None


class CommandeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    client_id: int
    mesure_id: int | None
    statut: str
    date_commande: date
    date_livraison_prevue: date | None
    date_livraison_reelle: date | None
    remise: int
    montant_total: int
    montant_paye: int
    notes: str | None
    cree_par_id: int
    lignes: list[LigneCommandeRead]
historiques_statuts: list[HistoriqueStatutRead] = Field(default_factory=list)
class CommandeListItem(BaseModel):
    commande: CommandeRead
    client_nom: str | None
    solde: int
    en_retard: bool


class CommandeListResponse(BaseModel):
    items: list[CommandeListItem]
    total: int
    limit: int
    offset: int