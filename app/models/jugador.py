from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Jugador(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    user = relationship("User", back_populates="jugador")
    
    inventory = relationship("Inventory", back_populates="jugador", cascade="all, delete-orphan")
    ship_rooms = relationship("ShipRoom", back_populates="jugador", cascade="all, delete-orphan")