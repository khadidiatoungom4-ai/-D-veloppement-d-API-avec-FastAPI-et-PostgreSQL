
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Paiement(Base):
    __tablename__ = "paiements"

    id: Mapped[int] = mapped_column(primary_key=True)

    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id"),
        nullable=False,
        index=True,
    )

    montant: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    date_paiement: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    enregistre_par_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    commande: Mapped["Commande"] = relationship(
        back_populates="paiements",
    )
