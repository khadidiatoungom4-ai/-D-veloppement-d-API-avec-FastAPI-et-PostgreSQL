from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commande import Commande
from app.models.paiement import Paiement
from app.schemas.paiement import PaiementCreate


def enregistrer_paiement(
    db: Session,
    commande_id: int,
    paiement_data: PaiementCreate,
    utilisateur_id: int,
) -> Paiement:

    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )

    if commande.statut == "annulee":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible d'enregistrer un paiement sur une commande annulée.",
        )

    date_paiement = paiement_data.date_paiement or date.today()

    if date_paiement > date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date du paiement ne peut pas être dans le futur.",
        )

    solde = commande.montant_total - commande.montant_paye

    if paiement_data.montant > solde:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le montant du paiement dépasse le solde restant.",
        )

    paiement = Paiement(
        commande_id=commande_id,
        montant=paiement_data.montant,
        mode=paiement_data.mode,
        reference=paiement_data.reference,
        date_paiement=date_paiement,
        enregistre_par_id=utilisateur_id,
    )

    commande.montant_paye += paiement_data.montant

    db.add(paiement)
    db.commit()
    db.refresh(paiement)

    return paiement


def lister_paiements(
    db: Session,
    commande_id: int,
) -> list[Paiement]:

    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )

    requete = (
        select(Paiement)
        .where(Paiement.commande_id == commande_id)
        .order_by(Paiement.date_paiement, Paiement.created_at)
    )

    return list(db.scalars(requete).all())


def annuler_paiement(
    db: Session,
    paiement_id: int,
) -> None:

    paiement = db.get(Paiement, paiement_id)

    if paiement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paiement introuvable.",
        )

    commande = db.get(Commande, paiement.commande_id)

    commande.montant_paye -= paiement.montant

    db.delete(paiement)
    db.commit()