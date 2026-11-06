from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UtilisateurConnecte(BaseModel):
    id: int
    email: str
    nom_complet: str
    role: str
    actif: bool