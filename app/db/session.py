# app/db/session.py
import os
from dotenv import load_dotenv

# Cargar variables desde .env en la raíz del proyecto
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Construcción de DATABASE_URL desde variables de entorno
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "galactum_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine de SQLAlchemy (con future=True para API moderna)
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session local (factory de sesiones)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base declarativa para los modelos
Base = declarative_base()

# Dependency para endpoints (yield generator)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
