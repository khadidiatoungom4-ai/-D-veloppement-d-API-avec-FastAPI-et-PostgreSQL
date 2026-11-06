
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LigneCommande(Base):
    __tablename__ = "lignes_commande"

    id: Mapped[int] = mapped_column(primary_key=True)

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        nullable=False,
        index=True,
    )

    type_vetement_id: Mapped[int] = mapped_column(
        ForeignKey("types_vetement.id"),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    quantite: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    prix_unitaire: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    commande: Mapped["Commande"] = relationship(
        back_populates="lignes"
    )