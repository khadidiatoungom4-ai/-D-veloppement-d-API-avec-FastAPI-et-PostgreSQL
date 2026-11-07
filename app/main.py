
from fastapi import FastAPI
from app.routers import clients, auth, utilisateurs, catalogue, paiements
from app.routers.mesures import router as mesures_router
from app.routers import commandes

# Création de l'application FastAPI
app = FastAPI(
    title="API de gestion d'un atelier de couture",
    description="API REST pour gérer les clients, les mesures, les commandes, les paiements et les livraisons d'un atelier de couture.",
    version="1.0.0"
)

app.include_router(clients.router)
app.include_router(auth.router)
app.include_router(utilisateurs.router)
app.include_router(catalogue.router)
app.include_router(mesures_router, prefix="/api/v1")
app.include_router(commandes.router)
app.include_router(paiements.router, prefix="/api/v1")

# Route d'accueil
@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur l'API de gestion de l'atelier de couture"
    }


# Route de vérification de l'API
@app.get("/health")
def health():
    return {
        "status": "ok"
    }

