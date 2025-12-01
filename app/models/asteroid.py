# app/models/asteroid.py
from sqlalchemy import Column, String, Float, Integer
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class Asteroid(Base):
    __tablename__ = "asteroids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # CORRECCIÓN 1: "asteroid_id" en lugar de "asteroidId"
    asteroid: Mapped[str] = mapped_column("asteroid", String, unique=True, index=True, nullable=False)
    
    # CORRECCIÓN 2: Mapear "pos_x" de la BD al atributo "position_x" de Python
    position_x: Mapped[float] = mapped_column("pos_x", Float, nullable=False)
    
    # CORRECCIÓN 3: Mapear "pos_y" de la BD al atributo "position_y" de Python
    position_y: Mapped[float] = mapped_column("pos_y", Float, nullable=False)
    
    # CORRECCIÓN 4: "resource_type" en lugar de "resourceType"
    resource_type: Mapped[str] = mapped_column("resource_type", String, nullable=False)

    cantidad_restante: Mapped[int] = mapped_column("cantidad_restante", Integer, nullable=False, default=3)

    #Incorporar variable de dureza para que cambie el tiempo de minado entre asteroides.