# app/models/jugador.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base import Base

class Jugador(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, index=True)
    
    # Clave foránea al modelo User (asumiendo que la tabla se llama 'users')
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Relación para poder acceder al usuario desde el jugador
    user = relationship("User", back_populates="jugador")

    # --- Línea que solicitaste ---
    # Almacena los recursos del jugador como un string JSON.
    # Ejemplo: '{"Roderitium": 1000, "Kliptium": 500}'
    inventario = Column(String, default='{}')