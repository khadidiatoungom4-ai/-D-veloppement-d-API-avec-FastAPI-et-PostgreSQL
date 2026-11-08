
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    DateTime,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    __table_args__ = (
        CheckConstraint(
            "genre IS NULL OR genre IN ('homme', 'femme', 'enfant')",
            name="ck_clients_genre",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    nom: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    prenom: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    telephone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    adresse: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    genre: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    commandes: Mapped[list["Commande"]] = relationship(
        back_populates="client"
    )