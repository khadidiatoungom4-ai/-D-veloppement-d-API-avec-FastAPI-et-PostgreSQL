from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.mesure import Mesure
from app.models.commande import Commande
from app.models.ligne_commande import LigneCommande
from app.models.type_vetement import TypeVetement
from app.schemas.commande import (
    CommandeCreate,
    CommandeUpdate,
    CommandeStatutUpdate,
)
from app.schemas.ligne_commande import LigneCommandeCreate

from app.models.historique_statut import HistoriqueStatut
def creer_commande(
    db: Session,
    donnees: CommandeCreate,
    utilisateur_id: int,
):
    # Vérifier que le client existe
    client = db.get(Client, donnees.client_id)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client introuvable.",
        )

    # Vérifier ou récupérer la mesure du client
    mesure_id = donnees.mesure_id

    if mesure_id is None:
        derniere_mesure = (
            db.query(Mesure)
            .filter(Mesure.client_id == donnees.client_id)
            .order_by(
                Mesure.date_prise.desc(),
                Mesure.id.desc(),
            )
            .first()
        )

        if derniere_mesure is not None:
            mesure_id = derniere_mesure.id

    else:
        mesure = db.get(Mesure, mesure_id)

        if mesure is None or mesure.client_id != donnees.client_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La mesure sélectionnée n'appartient pas à ce client.",
            )

    # Préparer les lignes et récupérer les délais
    lignes_a_creer = []
    delais = []

    for ligne in donnees.lignes:
        type_vetement = db.get(
            TypeVetement,
            ligne.type_vetement_id,
        )

        if type_vetement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Type de vêtement introuvable.",
            )

        if not type_vetement.actif:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce type de vêtement est inactif et ne peut pas être commandé.",
            )

        prix = (
            ligne.prix_unitaire
            if ligne.prix_unitaire is not None
            else type_vetement.prix_base
        )

        lignes_a_creer.append({
            "type_vetement_id": type_vetement.id,
            "description": ligne.description,
            "quantite": ligne.quantite,
            "prix_unitaire": prix,
        })

        delais.append(type_vetement.delai_jours)

    # Calculer le montant total
    montant_brut = sum(
        ligne["quantite"] * ligne["prix_unitaire"]
        for ligne in lignes_a_creer
    )

    if donnees.remise > montant_brut:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La remise ne peut pas dépasser le montant total.",
        )

    montant_total = montant_brut - donnees.remise

    # Calculer la date de livraison prévue
    date_livraison = donnees.date_livraison_prevue

    if date_livraison is None:
        delai_max = max(delais)
        date_livraison = date.today() + timedelta(days=delai_max)

    if date_livraison < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de livraison prévue ne peut pas précéder la date de commande.",
        )

    # Générer le numéro de commande
    annee = date.today().year
    prefixe = f"CMD-{annee}-"

    derniere_commande = (
        db.query(Commande)
        .filter(Commande.numero.like(f"{prefixe}%"))
        .order_by(Commande.numero.desc())
        .first()
    )

    if derniere_commande is None:
        prochain_numero = 1
    else:
        dernier_numero = int(derniere_commande.numero.split("-")[-1])
        prochain_numero = dernier_numero + 1

    numero_commande = f"{prefixe}{prochain_numero:05d}"

    # Créer la commande
    commande = Commande(
        numero=numero_commande,
        client_id=donnees.client_id,
        mesure_id=mesure_id,
        statut="en_attente",
        date_livraison_prevue=date_livraison,
        remise=donnees.remise,
        montant_total=montant_total,
        montant_paye=0,
        notes=donnees.notes,
        cree_par_id=utilisateur_id,
    )

    db.add(commande)
    db.flush()
    # Créer les lignes de la commande
    for ligne in lignes_a_creer:
        nouvelle_ligne = LigneCommande(
            commande_id=commande.id,
            type_vetement_id=ligne["type_vetement_id"],
            description=ligne["description"],
            quantite=ligne["quantite"],
            prix_unitaire=ligne["prix_unitaire"],
        )

        db.add(nouvelle_ligne)

    # Enregistrer le statut initial dans l'historique
    historique = HistoriqueStatut(
        commande_id=commande.id,
        ancien_statut=None,
        nouveau_statut="en_attente",
        commentaire="Création de la commande.",
        utilisateur_id=utilisateur_id,
    )

    db.add(historique)
    
   

    # Enregistrer la commande, ses lignes et son historique
    db.commit()
    db.refresh(commande)

    return commande
def lister_commandes(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    statut: str | None = None,
):
    requete = db.query(Commande)

    if statut is not None:
        requete = requete.filter(Commande.statut == statut)

    total = requete.count()

    commandes = (
        requete
        .order_by(Commande.date_commande.desc(), Commande.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    resultats = []

    for commande in commandes:
        client = db.get(Client, commande.client_id)

        nom_client = (
            f"{client.prenom} {client.nom}"
            if client
            else None
        )

        solde = commande.montant_total - commande.montant_paye

        en_retard = (
            commande.date_livraison_prevue is not None
            and commande.date_livraison_prevue < date.today()
            and commande.statut not in ["livree", "annulee"]
        )

        resultats.append({
            "commande": commande,
            "client_nom": nom_client,
            "solde": solde,
            "en_retard": en_retard,
        })

    return {
        "items": resultats,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
def obtenir_commande_par_id(db: Session, commande_id: int):
    commande = db.get(Commande, commande_id)

    if commande is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande introuvable.",
        )

    return commande
def modifier_commande(
    db: Session,
    commande_id: int,
    donnees: CommandeUpdate,
):
    commande = obtenir_commande_par_id(db, commande_id)

    if commande.statut in ["livree", "annulee"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une commande livrée ou annulée ne peut plus être modifiée.",
        )

    modifications = donnees.model_dump(exclude_unset=True)

    if "mesure_id" in modifications and modifications["mesure_id"] is not None:
        mesure = db.get(Mesure, modifications["mesure_id"])

        if mesure is None or mesure.client_id != commande.client_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cette mesure n'appartient pas au client de la commande.",
            )

    nouvelle_date = modifications.get(
        "date_livraison_prevue",
        commande.date_livraison_prevue,
    )

    if nouvelle_date is not None and nouvelle_date < commande.date_commande:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de livraison ne peut pas précéder la date de commande.",
        )

    nouvelle_remise = modifications.get("remise", commande.remise)

    montant_brut = sum(
        ligne.quantite * ligne.prix_unitaire
        for ligne in commande.lignes
    )

    if nouvelle_remise > montant_brut:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La remise ne peut pas dépasser le montant des prestations.",
        )

    nouveau_total = montant_brut - nouvelle_remise

    if nouveau_total < commande.montant_paye:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le nouveau montant ne peut pas être inférieur au montant déjà payé.",
        )

    for champ, valeur in modifications.items():
        setattr(commande, champ, valeur)

    commande.montant_total = nouveau_total

    db.commit()
    db.refresh(commande)

    return commande

def ajouter_ligne_commande(
    db: Session,
    commande_id: int,
    donnees: LigneCommandeCreate,
):
    commande = obtenir_commande_par_id(db, commande_id)

    if commande.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Les lignes ne peuvent être modifiées que lorsque la commande est en attente.",
        )

    type_vetement = db.get(
        TypeVetement,
        donnees.type_vetement_id,
    )

    if type_vetement is None or not type_vetement.actif:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Type de vêtement introuvable ou inactif.",
        )

    prix = donnees.prix_unitaire

    if prix is None:
        prix = type_vetement.prix_base

    nouvelle_ligne = LigneCommande(
        commande_id=commande.id,
        type_vetement_id=type_vetement.id,
        description=donnees.description,
        quantite=donnees.quantite,
        prix_unitaire=prix,
    )

    nouveau_montant_brut = (
        commande.montant_total
        + commande.remise
        + (donnees.quantite * prix)
    )

    nouveau_total = nouveau_montant_brut - commande.remise

    if nouveau_total < commande.montant_paye:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le nouveau montant ne peut pas être inférieur au montant déjà payé.",
        )

    db.add(nouvelle_ligne)
    commande.montant_total = nouveau_total

    db.commit()
    db.refresh(commande)

    return commande
def supprimer_ligne_commande(
    db: Session,
    commande_id: int,
    ligne_id: int,
):
    commande = obtenir_commande_par_id(db, commande_id)

    if commande.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Les lignes ne peuvent être modifiées que lorsque la commande est en attente.",
        )

    ligne = (
        db.query(LigneCommande)
        .filter(
            LigneCommande.id == ligne_id,
            LigneCommande.commande_id == commande_id,
        )
        .first()
    )

    if ligne is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne de commande introuvable.",
        )

    if len(commande.lignes) <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une commande doit conserver au moins une ligne.",
        )

    montant_brut = sum(
        element.quantite * element.prix_unitaire
        for element in commande.lignes
        if element.id != ligne_id
    )

    nouveau_total = montant_brut - commande.remise

    if nouveau_total < commande.montant_paye:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La suppression ferait passer le montant total sous le montant déjà payé.",
        )

    db.delete(ligne)
    commande.montant_total = nouveau_total

    db.commit()
    db.refresh(commande)

    return commande
def changer_statut_commande(
    db: Session,
    commande_id: int,
    donnees: CommandeStatutUpdate,
    utilisateur_id: int,
    role: str,
):
    commande = obtenir_commande_par_id(db, commande_id)

    transitions_autorisees = {
        "en_attente": ["en_coupe", "annulee"],
        "en_coupe": ["en_couture", "annulee"],
        "en_couture": ["essayage", "terminee", "annulee"],
        "essayage": ["retouches", "terminee", "annulee"],
        "retouches": ["essayage", "terminee", "annulee"],
        "terminee": [],
        "livree": [],
        "annulee": [],
    }

    ancien_statut = commande.statut
    nouveau_statut = donnees.statut

    if nouveau_statut == ancien_statut:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La commande possède déjà ce statut.",
        )

    if nouveau_statut == "livree":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une commande ne peut être livrée que par la confirmation de livraison.",
        )

    statuts_possibles = transitions_autorisees.get(ancien_statut, [])

    if nouveau_statut not in statuts_possibles:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transition de statut non autorisée.",
        )

    if role == "tailleur" and nouveau_statut == "annulee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un tailleur ne peut pas annuler une commande.",
        )

    if nouveau_statut == "annulee" and commande.montant_paye > 0:
        if not donnees.commentaire or not donnees.commentaire.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Un commentaire expliquant le remboursement ou l'avoir est obligatoire.",
            )

    commande.statut = nouveau_statut

    historique = HistoriqueStatut(
        commande_id=commande.id,
        ancien_statut=ancien_statut,
        nouveau_statut=nouveau_statut,
        commentaire=donnees.commentaire,
        utilisateur_id=utilisateur_id,
    )

    db.add(historique)
    db.commit()
    db.refresh(commande)

    return commande
def obtenir_historique_statuts(
    db: Session,
    commande_id: int,
):
    commande = obtenir_commande_par_id(db, commande_id)

    return (
        db.query(HistoriqueStatut)
        .filter(HistoriqueStatut.commande_id == commande.id)
        .order_by(
            HistoriqueStatut.date_changement.asc(),
            HistoriqueStatut.id.asc(),
        )
        .all()
    )