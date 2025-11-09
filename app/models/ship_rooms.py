from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class ShipRoom(Base):
    __tablename__ = "ship_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    room_id = Column(String, nullable=False) # Ej: "Armeria", "Fabrica"
    level = Column(Integer, default=1, nullable=False)
    
    # (Podríamos añadir un UniqueConstraint para player_id y room_id)
