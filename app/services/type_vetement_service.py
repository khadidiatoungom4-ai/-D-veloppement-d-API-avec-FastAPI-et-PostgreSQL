from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.type_vetement import TypeVetement
from app.schemas.type_vetement import TypeVetementCreate, TypeVetementUpdate


def creer_type_vetement(
    db: Session,
    donnees: TypeVetementCreate
) -> TypeVetement:
    nom_normalise = donnees.nom.strip()

    requete = select(TypeVetement).where(
        func.lower(TypeVetement.nom) == nom_normalise.lower()
    )
    type_existant = db.scalar(requete)

    if type_existant:
        raise HTTPException(
            status_code=409,
            detail="Ce type de vêtement existe déjà."
        )

    nouveau_type = TypeVetement(
        nom=nom_normalise,
        description=donnees.description,
        prix_base=donnees.prix_base,
        delai_jours=donnees.delai_jours,
        actif=True
    )

    db.add(nouveau_type)
    db.commit()
    db.refresh(nouveau_type)

    return nouveau_type


def lister_types_vetement(db: Session) -> list[TypeVetement]:
    requete = select(TypeVetement).order_by(TypeVetement.nom.asc())
    return list(db.scalars(requete).all())


def obtenir_type_vetement(
    db: Session,
    type_vetement_id: int
) -> TypeVetement:
    requete = select(TypeVetement).where(
        TypeVetement.id == type_vetement_id
    )
    type_vetement = db.scalar(requete)

    if type_vetement is None:
        raise HTTPException(
            status_code=404,
            detail="Type de vêtement introuvable."
        )

    return type_vetement


def modifier_type_vetement(
    db: Session,
    type_vetement_id: int,
    donnees: TypeVetementUpdate
) -> TypeVetement:
    type_vetement = obtenir_type_vetement(db, type_vetement_id)
    modifications = donnees.model_dump(exclude_unset=True)

    if "nom" in modifications and modifications["nom"] is not None:
        nom_normalise = modifications["nom"].strip()

        requete = select(TypeVetement).where(
            func.lower(TypeVetement.nom) == nom_normalise.lower(),
            TypeVetement.id != type_vetement_id
        )
        type_existant = db.scalar(requete)

        if type_existant:
            raise HTTPException(
                status_code=409,
                detail="Ce nom est déjà utilisé par un autre type de vêtement."
            )

        modifications["nom"] = nom_normalise

    for champ, valeur in modifications.items():
        setattr(type_vetement, champ, valeur)

    db.commit()
    db.refresh(type_vetement)

    return type_vetement