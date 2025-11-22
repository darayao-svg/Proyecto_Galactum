# app/models/crafting.py
from sqlalchemy import Column, String, Text, JSON
from ..db.base import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # 'fabrica' o 'armeria'
    
    # Almacenamos los ingredientes como un JSON.
    # Ejemplo: '[{"item_id": "Roderitium", "quantity": 10}]'
    ingredients = Column(JSON, nullable=False)