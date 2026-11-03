
from fastapi import FastAPI

# Création de l'application FastAPI
app = FastAPI(
    title="API de gestion d'un atelier de couture",
    description="API REST pour gérer les clients, les mesures, les commandes, les paiements et les livraisons d'un atelier de couture.",
    version="1.0.0"
)


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
