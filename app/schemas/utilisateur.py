
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Schéma pour créer un utilisateur
class UtilisateurCreate(BaseModel):
    email: EmailStr
    nom_complet: str = Field(min_length=1, max_length=200)
    mot_de_passe: str = Field(min_length=8)
    role: Literal["admin", "accueil", "tailleur"] = "accueil"


# Schéma pour modifier un utilisateur
class UtilisateurUpdate(BaseModel):
    nom_complet: str | None = Field(default=None, min_length=1, max_length=200)
    mot_de_passe: str | None = Field(default=None, min_length=8)
    role: Literal["admin", "accueil", "tailleur"] | None = None
    actif: bool | None = None


# Schéma pour retourner les informations d'un utilisateur
class UtilisateurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nom_complet: str
    role: str
    actif: bool
    created_at: datetime
class UtilisateurListResponse(BaseModel):
    items: list[UtilisateurRead]
    total: int
    limit: int
    offset: int

