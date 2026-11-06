from sqlalchemy import Boolean, CheckConstraint, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TypeVetement(Base):
    __tablename__ = "types_vetement"

    __table_args__ = (
        CheckConstraint("prix_base >= 0", name="ck_types_vetement_prix_base"),
        CheckConstraint("delai_jours > 0", name="ck_types_vetement_delai_jours"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prix_base: Mapped[int] = mapped_column(Integer, nullable=False)
    delai_jours: Mapped[int] = mapped_column(Integer, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)