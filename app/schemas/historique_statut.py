from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoriqueStatutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    commande_id: int
    ancien_statut: str | None
    nouveau_statut: str
    commentaire: str | None
    utilisateur_id: int
    date_changement: datetime