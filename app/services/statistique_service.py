from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.commande import Commande
from app.models.paiement import Paiement
from app.models.livraison import Livraison

from app.schemas.statistique import (
    TableauBordRead,
    StatutCommandeStatistique,
)
from sqlalchemy import case
from app.schemas.statistique import ChiffreAffairesStatistiqueResponse
from app.models.ligne_commande import LigneCommande
from app.models.type_vetement import TypeVetement
from app.schemas.statistique import TypesVetementStatistiqueResponse
from app.schemas.statistique import TopClientsStatistiqueResponse

from app.schemas.statistique import CommandesImpayeesStatistiqueResponse
from app.models.client import Client

def obtenir_tableau_de_bord(db: Session) -> TableauBordRead:
    aujourd_hui = date.today()
    debut_mois = aujourd_hui.replace(day=1)

    # 1. Chiffre d'affaires du mois
    chiffre_affaires_mois = (
        db.query(func.coalesce(func.sum(Commande.montant_total), 0))
        .filter(
            Commande.date_commande >= debut_mois,
            Commande.date_commande <= aujourd_hui,
            Commande.statut != "annulee",
        )
        .scalar()
    )

    # 2. Encaissements du mois
    encaisse_mois = (
        db.query(func.coalesce(func.sum(Paiement.montant), 0))
        .filter(
            Paiement.date_paiement >= debut_mois,
            Paiement.date_paiement <= aujourd_hui,
        )
        .scalar()
    )

    # 3. Nombre de commandes du mois
    nb_commandes_mois = (
        db.query(func.count(Commande.id))
        .filter(
            Commande.date_commande >= debut_mois,
            Commande.date_commande <= aujourd_hui,
        )
        .scalar()
    )

    # 4. Reste total à encaisser
    reste_a_encaisser = (
        db.query(
            func.coalesce(
                func.sum(Commande.montant_total - Commande.montant_paye), 0
            )
        )
        .filter(Commande.statut != "annulee")
        .scalar()
    )

    # 5. Nombre de commandes par statut
    statuts = [
        "en_attente",
        "en_coupe",
        "en_couture",
        "essayage",
        "retouches",
        "terminee",
        "livree",
        "annulee",
    ]

    resultats_statuts = (
        db.query(Commande.statut, func.count(Commande.id))
        .group_by(Commande.statut)
        .all()
    )

    comptes_statuts = {
        statut: nombre for statut, nombre in resultats_statuts
    }

    commandes_par_statut = [
        StatutCommandeStatistique(
            statut=statut,
            nombre=comptes_statuts.get(statut, 0),
        )
        for statut in statuts
    ]

    # 6. Commandes en retard
    nb_commandes_en_retard = (
        db.query(func.count(Commande.id))
        .filter(
            Commande.date_livraison_prevue < aujourd_hui,
            Commande.statut.notin_(["livree", "annulee"]),
        )
        .scalar()
    )

    # 7. Commandes prêtes à livrer
    commandes_pretes_a_livrer = (
        db.query(func.count(Commande.id))
        .filter(Commande.statut == "terminee")
        .scalar()
    )

    # 8. Livraisons prévues aujourd'hui
    livraisons_du_jour = (
        db.query(func.count(Livraison.id))
        .filter(
            Livraison.date_prevue == aujourd_hui,
            Livraison.statut == "planifiee",
        )
        .scalar()
    )

    return TableauBordRead(
        chiffre_affaires_mois=chiffre_affaires_mois,
        encaisse_mois=encaisse_mois,
        nb_commandes_mois=nb_commandes_mois,
        reste_a_encaisser=reste_a_encaisser,
        commandes_par_statut=commandes_par_statut,
        nb_commandes_en_retard=nb_commandes_en_retard,
        commandes_pretes_a_livrer=commandes_pretes_a_livrer,
        livraisons_du_jour=livraisons_du_jour,
    )
def obtenir_chiffre_affaires(
    db: Session,
    granularite: str,
    date_debut: date,
    date_fin: date,
) -> ChiffreAffairesStatistiqueResponse:

    if date_debut > date_fin:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="La date de début doit être antérieure ou égale à la date de fin.",
        )

    if granularite == "jour":
        periode = func.to_char(Commande.date_commande, "YYYY-MM-DD")
        periode_paiement = func.to_char(Paiement.date_paiement, "YYYY-MM-DD")
    else:
        periode = func.to_char(Commande.date_commande, "YYYY-MM")
        periode_paiement = func.to_char(Paiement.date_paiement, "YYYY-MM")

    commandes = (
        db.query(
            periode.label("periode"),
            func.sum(Commande.montant_total).label("chiffre_affaires"),
        )
        .filter(
            Commande.date_commande >= date_debut,
            Commande.date_commande <= date_fin,
            Commande.statut != "annulee",
        )
        .group_by(periode)
        .all()
    )

    paiements = (
        db.query(
            periode_paiement.label("periode"),
            func.sum(Paiement.montant).label("encaisse"),
        )
        .join(Commande, Paiement.commande_id == Commande.id)
        .filter(
            Paiement.date_paiement >= date_debut,
            Paiement.date_paiement <= date_fin,
            Commande.statut != "annulee",
        )
        .group_by(periode_paiement)
        .all()
    )

    resultats = {}

    for ligne in commandes:
        resultats[ligne.periode] = {
            "chiffre_affaires": int(ligne.chiffre_affaires or 0),
            "encaisse": 0,
        }

    for ligne in paiements:
        if ligne.periode not in resultats:
            resultats[ligne.periode] = {
                "chiffre_affaires": 0,
                "encaisse": int(ligne.encaisse or 0),
            }
        else:
            resultats[ligne.periode]["encaisse"] = int(ligne.encaisse or 0)

    items = [
        {
            "periode": periode,
            "chiffre_affaires": valeurs["chiffre_affaires"],
            "encaisse": valeurs["encaisse"],
        }
        for periode, valeurs in sorted(resultats.items())
    ]

    return ChiffreAffairesStatistiqueResponse(
        granularite=granularite,
        date_debut=date_debut,
        date_fin=date_fin,
        items=items,
    )
def obtenir_statistiques_types_vetement(
    db: Session,
    date_debut: date,
    date_fin: date,
) -> TypesVetementStatistiqueResponse:

    if date_debut > date_fin:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="La date de début doit être antérieure ou égale à la date de fin.",
        )

    resultats = (
        db.query(
            TypeVetement.id.label("type_vetement_id"),
            TypeVetement.nom.label("nom_type"),
            func.coalesce(func.sum(LigneCommande.quantite), 0).label(
                "quantite_vendue"
            ),
            func.coalesce(
                func.sum(LigneCommande.quantite * LigneCommande.prix_unitaire),
                0,
            ).label("chiffre_affaires"),
        )
        .join(
            LigneCommande,
            LigneCommande.type_vetement_id == TypeVetement.id,
        )
        .join(Commande, Commande.id == LigneCommande.commande_id)
        .filter(
            Commande.date_commande >= date_debut,
            Commande.date_commande <= date_fin,
            Commande.statut != "annulee",
        )
        .group_by(TypeVetement.id, TypeVetement.nom)
        .order_by(
            func.sum(LigneCommande.quantite * LigneCommande.prix_unitaire).desc()
        )
        .all()
    )

    items = [
        {
            "type_vetement_id": ligne.type_vetement_id,
            "nom_type": ligne.nom_type,
            "quantite_vendue": int(ligne.quantite_vendue),
            "chiffre_affaires": int(ligne.chiffre_affaires),
        }
        for ligne in resultats
    ]

    return TypesVetementStatistiqueResponse(
        date_debut=date_debut,
        date_fin=date_fin,
        items=items,
    )
def obtenir_top_clients(
    db: Session,
    date_debut: date,
    date_fin: date,
    limite: int = 10,
) -> TopClientsStatistiqueResponse:

    if date_debut > date_fin:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="La date de début doit être antérieure ou égale à la date de fin.",
        )

    from app.models.client import Client

    resultats = (
        db.query(
            Client.id.label("client_id"),
            Client.nom,
            Client.prenom,
            Client.telephone,
            func.count(Commande.id).label("nb_commandes"),
            func.coalesce(func.sum(Commande.montant_total), 0).label(
                "chiffre_affaires"
            ),
            func.coalesce(
                func.sum(Commande.montant_total - Commande.montant_paye), 0
            ).label("solde_du"),
        )
        .join(Commande, Commande.client_id == Client.id)
        .filter(
            Commande.date_commande >= date_debut,
            Commande.date_commande <= date_fin,
            Commande.statut != "annulee",
        )
        .group_by(Client.id, Client.nom, Client.prenom, Client.telephone)
        .order_by(func.sum(Commande.montant_total).desc())
        .limit(limite)
        .all()
    )

    items = [
        {
            "client_id": ligne.client_id,
            "client_nom": f"{ligne.nom} {ligne.prenom}",
            "client_telephone": ligne.telephone,
            "nb_commandes": int(ligne.nb_commandes),
            "chiffre_affaires": int(ligne.chiffre_affaires),
            "solde_du": int(ligne.solde_du),
        }
        for ligne in resultats
    ]

    return TopClientsStatistiqueResponse(
        date_debut=date_debut,
        date_fin=date_fin,
        items=items,
    )
def obtenir_commandes_impayees(
    db: Session,
    limit: int = 20,
    offset: int = 0,
) -> CommandesImpayeesStatistiqueResponse:

    aujourd_hui = date.today()

    requete = (
        db.query(Commande, Client)
        .join(Client, Client.id == Commande.client_id)
        .filter(
            Commande.statut != "annulee",
            Commande.montant_paye < Commande.montant_total,
        )
    )

    total = requete.count()

    commandes = (
        requete
        .order_by(
            Commande.date_livraison_prevue.asc().nullslast(),
            Commande.date_commande.asc(),
        )
        .limit(limit)
        .offset(offset)
        .all()
    )

    items = [
        {
            "id": commande.id,
            "numero": commande.numero,
            "client_nom": f"{client.nom} {client.prenom}",
            "client_telephone": client.telephone,
            "date_commande": commande.date_commande,
            "date_livraison_prevue": commande.date_livraison_prevue,
            "montant_total": commande.montant_total,
            "montant_paye": commande.montant_paye,
            "solde": commande.montant_total - commande.montant_paye,
            "en_retard": (
                commande.date_livraison_prevue is not None
                and commande.date_livraison_prevue < aujourd_hui
                and commande.statut not in ["livree", "annulee"]
            ),
        }
        for commande, client in commandes
    ]

    return CommandesImpayeesStatistiqueResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )