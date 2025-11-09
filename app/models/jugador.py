# app/models/jugador.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..db.base import Base

class Jugador(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, index=True)
    
    # Clave foránea al modelo User. Debe ser UUID para coincidir con users.id
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Relación para poder acceder al usuario desde el jugador
    user = relationship("User", back_populates="jugador")

    # Relación para acceder al inventario del jugador
    inventario = relationship("InventarioJugador", back_populates="jugador", cascade="all, delete-orphan")