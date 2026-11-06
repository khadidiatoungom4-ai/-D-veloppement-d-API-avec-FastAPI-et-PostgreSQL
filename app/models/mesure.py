from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Mesure(Base):
    __tablename__ = "mesures"

    __table_args__ = (
        CheckConstraint(
            "taille_cm IS NULL OR (taille_cm > 0 AND taille_cm <= 300)",
            name="ck_mesures_taille_cm",
        ),
        CheckConstraint(
            "tour_cou IS NULL OR (tour_cou > 0 AND tour_cou <= 300)",
            name="ck_mesures_tour_cou",
        ),
        CheckConstraint(
            "carrure_dos IS NULL OR (carrure_dos > 0 AND carrure_dos <= 300)",
            name="ck_mesures_carrure_dos",
        ),
        CheckConstraint(
            "longueur_epaule IS NULL OR (longueur_epaule > 0 AND longueur_epaule <= 300)",
            name="ck_mesures_longueur_epaule",
        ),
        CheckConstraint(
            "tour_poitrine IS NULL OR (tour_poitrine > 0 AND tour_poitrine <= 300)",
            name="ck_mesures_tour_poitrine",
        ),
        CheckConstraint(
            "tour_taille IS NULL OR (tour_taille > 0 AND tour_taille <= 300)",
            name="ck_mesures_tour_taille",
        ),
        CheckConstraint(
            "tour_bassin IS NULL OR (tour_bassin > 0 AND tour_bassin <= 300)",
            name="ck_mesures_tour_bassin",
        ),
        CheckConstraint(
            "longueur_manche IS NULL OR (longueur_manche > 0 AND longueur_manche <= 300)",
            name="ck_mesures_longueur_manche",
        ),
        CheckConstraint(
            "tour_bras IS NULL OR (tour_bras > 0 AND tour_bras <= 300)",
            name="ck_mesures_tour_bras",
        ),
        CheckConstraint(
            "tour_poignet IS NULL OR (tour_poignet > 0 AND tour_poignet <= 300)",
            name="ck_mesures_tour_poignet",
        ),
        CheckConstraint(
            "longueur_dos IS NULL OR (longueur_dos > 0 AND longueur_dos <= 300)",
            name="ck_mesures_longueur_dos",
        ),
        CheckConstraint(
            "longueur_haut IS NULL OR (longueur_haut > 0 AND longueur_haut <= 300)",
            name="ck_mesures_longueur_haut",
        ),
        CheckConstraint(
            "longueur_pantalon IS NULL OR (longueur_pantalon > 0 AND longueur_pantalon <= 300)",
            name="ck_mesures_longueur_pantalon",
        ),
        CheckConstraint(
            "tour_cuisse IS NULL OR (tour_cuisse > 0 AND tour_cuisse <= 300)",
            name="ck_mesures_tour_cuisse",
        ),
        CheckConstraint(
            "tour_genou IS NULL OR (tour_genou > 0 AND tour_genou <= 300)",
            name="ck_mesures_tour_genou",
        ),
        CheckConstraint(
            "bas_pantalon IS NULL OR (bas_pantalon > 0 AND bas_pantalon <= 300)",
            name="ck_mesures_bas_pantalon",
        ),
        CheckConstraint(
            "entrejambe IS NULL OR (entrejambe > 0 AND entrejambe <= 300)",
            name="ck_mesures_entrejambe",
        ),
        CheckConstraint(
            "longueur_robe IS NULL OR (longueur_robe > 0 AND longueur_robe <= 300)",
            name="ck_mesures_longueur_robe",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    date_prise: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    prise_par_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    taille_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_cou: Mapped[float | None] = mapped_column(Float, nullable=True)
    carrure_dos: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_epaule: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_poitrine: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_taille: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_bassin: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_manche: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_bras: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_poignet: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_dos: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_haut: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_pantalon: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_cuisse: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_genou: Mapped[float | None] = mapped_column(Float, nullable=True)
    bas_pantalon: Mapped[float | None] = mapped_column(Float, nullable=True)
    entrejambe: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_robe: Mapped[float | None] = mapped_column(Float, nullable=True)