from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    telephone: str = Field(min_length=6, max_length=25)
    email: str | None = None
    adresse: str | None = None
    genre: Literal["homme", "femme", "enfant"] | None = None
    notes: str | None = None


class ClientUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, min_length=1, max_length=100)
    telephone: str | None = Field(default=None, min_length=6, max_length=25)
    email: str | None = None
    adresse: str | None = None
    genre: Literal["homme", "femme", "enfant"] | None = None
    notes: str | None = None


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    telephone: str
    email: str | None
    adresse: str | None
    genre: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseModel):
    items: list[ClientRead]
    total: int
    limit: int
    offset: int