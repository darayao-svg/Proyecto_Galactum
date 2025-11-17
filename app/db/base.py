from sqlalchemy.orm import declarative_base

Base = declarative_base()

# IMPORTANTE: importa DESPUÉS de crear Base para evitar circular imports
from app.models.user import User
from app.models.jugador import Jugador
from app.models.server import Server