from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy.orm import relationship

class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(primary_key=True)

    numero: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    mesure_id: Mapped[int | None] = mapped_column(
        ForeignKey("mesures.id"),
        nullable=True,
    )

    statut: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="en_attente",
    )

    date_commande: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    date_livraison_prevue: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_livraison_reelle: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    remise: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    montant_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    montant_paye: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cree_par_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    lignes: Mapped[list["LigneCommande"]] = relationship(
        back_populates="commande",
        cascade="all, delete-orphan",
    )
    historiques_statuts: Mapped[list["HistoriqueStatut"]] = relationship(
    back_populates="commande",
    cascade="all, delete-orphan",
    )
    paiements: Mapped[list["Paiement"]] = relationship(
    back_populates="commande",
    cascade="all, delete-orphan",
    )
    livraison: Mapped["Livraison | None"] = relationship(
    back_populates="commande",
    uselist=False,
)