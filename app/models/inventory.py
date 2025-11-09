from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    resource_id = Column(String, nullable=False) # Ej: "Roderitium", "Kliptium", "Ore"
    quantity = Column(Integer, default=0, nullable=False)
    
    # (Aquí también un UniqueConstraint para player_id y resource_id)