from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Livraison(Base):
    __tablename__ = "livraisons"

    id: Mapped[int] = mapped_column(primary_key=True)

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        nullable=False,
        unique=True,
    )

    mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    adresse: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    livreur: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    date_prevue: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_effective: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    statut: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="planifiee",
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    commande: Mapped["Commande"] = relationship(
        back_populates="livraison",
    )
    