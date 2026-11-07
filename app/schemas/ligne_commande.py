
from pydantic import BaseModel, ConfigDict, Field


class LigneCommandeCreate(BaseModel):
    type_vetement_id: int
    description: str | None = None
    quantite: int = Field(gt=0)
    prix_unitaire: int | None = Field(default=None, gt=0)


class LigneCommandeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    commande_id: int
    type_vetement_id: int
    description: str | None
    quantite: int
    prix_unitaire: int
class LigneCommandeDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    commande_id: int
    type_vetement_id: int
    prestation_nom: str
    description: str | None
    quantite: int
    prix_unitaire: int
    sous_total: int