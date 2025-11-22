# app/models/tripulante.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Tripulante(Base):
    __tablename__ = "tripulantes"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("jugadores.id"), nullable=False)
    nombre = Column(String, nullable=False)
    nivel = Column(Integer, default=1, nullable=False)
    especializacion = Column(String, nullable=True)
    slot_id = Column(Integer, ForeignKey("ship_rooms.id"), nullable=True)

    jugador = relationship("Jugador", back_populates="tripulantes")
    room = relationship("ShipRoom")
