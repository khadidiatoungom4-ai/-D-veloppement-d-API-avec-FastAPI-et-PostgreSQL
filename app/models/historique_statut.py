from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HistoriqueStatut(Base):
    __tablename__ = "historiques_statuts"

    id: Mapped[int] = mapped_column(primary_key=True)

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        nullable=False,
        index=True,
    )

    ancien_statut: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    nouveau_statut: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    commentaire: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    date_changement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    commande: Mapped["Commande"] = relationship(
        back_populates="historiques_statuts",
    )