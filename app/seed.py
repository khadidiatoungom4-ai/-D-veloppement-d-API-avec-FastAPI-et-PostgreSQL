
import os

from sqlalchemy import select

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.models.type_vetement import TypeVetement
from app.core.security import hacher_mot_de_passe


CATALOGUE_INITIAL = [
    {
        "nom": "Boubou",
        "description": "Boubou homme en bazin ou brodé",
        "prix_base": 35000,
        "delai_jours": 10,
    },
    {
        "nom": "Costume 2 pièces",
        "description": "Veste et pantalon",
        "prix_base": 85000,
        "delai_jours": 14,
    },
    {
        "nom": "Robe",
        "description": "Robe sur mesure",
        "prix_base": 30000,
        "delai_jours": 7,
    },
    {
        "nom": "Ensemble wax",
        "description": "Tenue deux pièces en wax",
        "prix_base": 25000,
        "delai_jours": 7,
    },
    {
        "nom": "Chemise",
        "description": "Chemise sur mesure",
        "prix_base": 15000,
        "delai_jours": 5,
    },
    {
        "nom": "Pantalon",
        "description": "Pantalon sur mesure",
        "prix_base": 12000,
        "delai_jours": 4,
    },
    {
        "nom": "Retouche",
        "description": "Ourlet, rétrécissement, remplacement de fermeture",
        "prix_base": 3000,
        "delai_jours": 2,
    },
]


def creer_administrateur(db):
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    nom_complet = os.getenv("ADMIN_NOM_COMPLET", "").strip()
    mot_de_passe = os.getenv("ADMIN_PASSWORD", "")

    if not email or not nom_complet or not mot_de_passe:
        raise ValueError(
            "Les variables ADMIN_EMAIL, ADMIN_NOM_COMPLET "
            "et ADMIN_PASSWORD doivent être définies."
        )

    if len(mot_de_passe) < 8:
        raise ValueError(
            "Le mot de passe administrateur doit contenir "
            "au moins 8 caractères."
        )

    administrateur = db.scalar(
        select(Utilisateur).where(Utilisateur.email == email)
    )

    if administrateur:
        print("Administrateur déjà existant : aucune création.")
        return

    administrateur = Utilisateur(
        email=email,
        nom_complet=nom_complet,
        mot_de_passe_hash=hacher_mot_de_passe(mot_de_passe),
        role="admin",
        actif=True,
    )

    db.add(administrateur)
    print("Administrateur créé.")


def creer_catalogue(db):
    nombre_crees = 0

    for prestation in CATALOGUE_INITIAL:
        existant = db.scalar(
            select(TypeVetement).where(
                TypeVetement.nom == prestation["nom"]
            )
        )

        if existant:
            continue

        db.add(TypeVetement(**prestation, actif=True))
        nombre_crees += 1

    print(f"{nombre_crees} prestation(s) ajoutée(s) au catalogue.")


def initialiser_application():
    db = SessionLocal()

    try:
        creer_administrateur(db)
        creer_catalogue(db)

        db.commit()

        print("Initialisation terminée avec succès.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    initialiser_application()
