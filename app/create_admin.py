from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.core.security import hacher_mot_de_passe


def creer_administrateur():
    db = SessionLocal()

    try:
        email = input("Email de l'administrateur : ").strip().lower()

        utilisateur_existant = db.scalar(
            select(Utilisateur).where(Utilisateur.email == email)
        )

        if utilisateur_existant:
            print("Un compte existe déjà avec cet email.")
            return

        mot_de_passe = getpass("Mot de passe (8 caractères minimum) : ")

        if len(mot_de_passe) < 8:
            print("Le mot de passe doit contenir au moins 8 caractères.")
            return

        confirmation = getpass("Confirme le mot de passe : ")

        if mot_de_passe != confirmation:
            print("Les mots de passe ne correspondent pas.")
            return

        administrateur = Utilisateur(
            email=email,
            nom_complet=input("Nom complet : ").strip(),
            mot_de_passe_hash=hacher_mot_de_passe(mot_de_passe),
            role="admin",
            actif=True
        )

        db.add(administrateur)
        db.commit()

        print("Compte administrateur créé avec succès.")

    finally:
        db.close()


if __name__ == "__main__":
    creer_administrateur()