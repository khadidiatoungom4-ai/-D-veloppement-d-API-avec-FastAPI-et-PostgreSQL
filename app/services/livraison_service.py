from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.commande import Commande
from app.models.livraison import Livraison
from app.schemas.livraison import LivraisonCreate
from app.models.historique_statut import HistoriqueStatut
from app.schemas.livraison import LivraisonConfirmation
from app.models.client import Client

def planifier_livraison(
    db: Session,
    commande_id: int,
    donnees: LivraisonCreate,
) -> Livraison:

    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )

    if commande.statut in ["livree", "annulee"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de planifier une livraison pour cette commande.",
        )

    livraison = db.query(Livraison).filter(
        Livraison.commande_id == commande_id
    ).first()

    if livraison is None:
        livraison = Livraison(
            commande_id=commande_id,
            mode=donnees.mode,
            date_prevue=donnees.date_prevue,
            adresse=donnees.adresse,
            livreur=donnees.livreur,
            notes=donnees.notes,
            statut="planifiee",
        )

        db.add(livraison)

    else:
        livraison.mode = donnees.mode
        livraison.date_prevue = donnees.date_prevue
        livraison.adresse = donnees.adresse
        livraison.livreur = donnees.livreur
        livraison.notes = donnees.notes

    commande.date_livraison_prevue = donnees.date_prevue

    db.commit()
    db.refresh(livraison)

    return livraison


def obtenir_livraison(
    db: Session,
    commande_id: int,
) -> Livraison:

    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )

    livraison = db.query(Livraison).filter(
        Livraison.commande_id == commande_id
    ).first()

    if livraison is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune livraison planifiee pour cette commande.",
        )

    return livraison
def confirmer_livraison(
    db: Session,
    commande_id: int,
    donnees: LivraisonConfirmation,
    utilisateur_id: int,
) -> Livraison:

    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )

    # RG19 : la commande doit etre terminee.
    if commande.statut != "terminee":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La commande doit etre terminee avant sa livraison.",
        )

    date_effective = donnees.date_effective or date.today()

    # Calcul du solde restant.
    solde_restant = commande.montant_total - commande.montant_paye

    # RG19 : verifier le paiement integral.
    if solde_restant > 0 and not donnees.autoriser_solde_impaye:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Paiement incomplet. Solde restant : {solde_restant}.",
        )

    # Rechercher une livraison deja planifiee.
    livraison = db.query(Livraison).filter(
        Livraison.commande_id == commande_id
    ).first()

    # RG20 : creer automatiquement un retrait atelier si necessaire.
    if livraison is None:
        livraison = Livraison(
            commande_id=commande_id,
            mode="retrait_atelier",
            date_prevue=commande.date_livraison_prevue or date_effective,
            date_effective=date_effective,
            statut="livree",
        )
        db.add(livraison)

    else:
        livraison.date_effective = date_effective
        livraison.statut = "livree"

    # Mise a jour de la commande.
    ancien_statut = commande.statut
    commande.statut = "livree"
    commande.date_livraison_reelle = date_effective

    # Enregistrer le changement dans l'historique.
    commentaire = "Livraison confirmee."

    if solde_restant > 0:
        commentaire = (
            f"Livraison confirmee avec solde impaye autorise. "
            f"Solde restant : {solde_restant}."
        )

    historique = HistoriqueStatut(
        commande_id=commande.id,
        ancien_statut=ancien_statut,
        nouveau_statut="livree",
        commentaire=commentaire,
        utilisateur_id=utilisateur_id,
    )

    db.add(historique)

    db.commit()
    db.refresh(livraison)

    return livraison
def lister_livraisons(
    db: Session,
    statut_livraison: str | None = None,
    date_min: date | None = None,
    date_max: date | None = None,
) -> list[dict]:

    requete = (
        db.query(Livraison, Commande, Client)
        .join(Commande, Livraison.commande_id == Commande.id)
        .join(Client, Commande.client_id == Client.id)
    )

    if statut_livraison is not None:
        requete = requete.filter(
            Livraison.statut == statut_livraison
        )

    if date_min is not None:
        requete = requete.filter(
            Livraison.date_prevue >= date_min
        )

    if date_max is not None:
        requete = requete.filter(
            Livraison.date_prevue <= date_max
        )

    resultats = requete.order_by(
        Livraison.date_prevue.asc()
    ).all()

    livraisons = []

    for livraison, commande, client in resultats:
        livraisons.append({
            "id": livraison.id,
            "commande_id": livraison.commande_id,
            "mode": livraison.mode,
            "adresse": livraison.adresse,
            "livreur": livraison.livreur,
            "date_prevue": livraison.date_prevue,
            "date_effective": livraison.date_effective,
            "statut": livraison.statut,
            "notes": livraison.notes,
            "numero_commande": commande.numero,
            "client_nom": f"{client.nom} {client.prenom}",
            "client_telephone": client.telephone,
            "solde_commande": (
                commande.montant_total - commande.montant_paye
            ),
        })

    return livraisons