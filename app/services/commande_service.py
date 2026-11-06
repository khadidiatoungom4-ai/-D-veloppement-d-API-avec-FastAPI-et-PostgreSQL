from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.mesure import Mesure
from app.models.commande import Commande
from app.models.ligne_commande import LigneCommande
from app.models.type_vetement import TypeVetement

from app.schemas.commande import CommandeCreate, CommandeUpdate

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

    # Enregistrer la commande et ses lignes
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