from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from dotenv import load_dotenv
import os

# Charge les variables définies dans le fichier .env
load_dotenv()

# Récupère l'adresse de connexion à PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Crée le moteur de connexion à la base de données
engine = create_engine(DATABASE_URL)

# Prépare la création de sessions pour interagir avec la base
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# Classe de base de nos futurs modèles SQLAlchemy
class Base(DeclarativeBase):
    pass

