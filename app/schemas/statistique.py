from pydantic import BaseModel
from datetime import date

class StatutCommandeStatistique(BaseModel):
    statut: str
    nombre: int


class TableauBordRead(BaseModel):
    chiffre_affaires_mois: int
    encaisse_mois: int
    nb_commandes_mois: int
    reste_a_encaisser: int
    commandes_par_statut: list[StatutCommandeStatistique]
    nb_commandes_en_retard: int
    commandes_pretes_a_livrer: int
    livraisons_du_jour: int
class ChiffreAffairesPeriodeRead(BaseModel):
    periode: str
    chiffre_affaires: int
    encaisse: int


class ChiffreAffairesRead(BaseModel):
    granularite: str
    date_debut: date
    date_fin: date
    periodes: list[ChiffreAffairesPeriodeRead]    
class TypeVetementStatistiqueRead(BaseModel):
    type_vetement_id: int
    nom_type: str
    quantite_vendue: int
    chiffre_affaires: int


class TypesVetementStatistiqueResponse(BaseModel):
    date_debut: date
    date_fin: date
    items: list[TypeVetementStatistiqueRead]    
class TopClientStatistiqueRead(BaseModel):
    client_id: int
    client_nom: str
    client_telephone: str
    nb_commandes: int
    chiffre_affaires: int
    solde_du: int


class TopClientsStatistiqueResponse(BaseModel):
    date_debut: date
    date_fin: date
    items: list[TopClientStatistiqueRead]    
class CommandeImpayeStatistiqueRead(BaseModel):
    id: int
    numero: str
    client_nom: str
    client_telephone: str
    date_commande: date
    date_livraison_prevue: date | None
    montant_total: int
    montant_paye: int
    solde: int
    en_retard: bool    
class CommandesImpayeesStatistiqueResponse(BaseModel):
    items: list[CommandeImpayeStatistiqueRead]
    total: int
    limit: int
    offset: int
class ChiffreAffairesPeriodeRead(BaseModel):
    periode: str
    chiffre_affaires: int
    encaisse: int


class ChiffreAffairesStatistiqueResponse(BaseModel):
    granularite: str
    date_debut: date
    date_fin: date
    items: list[ChiffreAffairesPeriodeRead]