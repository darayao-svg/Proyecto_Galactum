# app/models/ship.py - CORREGIDO
from sqlalchemy import Column, Float, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Ship(Base):
    __tablename__ = "ships"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_moving = Column(Boolean, default=False)
    current_pos_x = Column(Float)
    current_pos_y = Column(Float)
    start_pos_x = Column(Float, nullable=True)
    start_pos_y = Column(Float, nullable=True)
    end_pos_x = Column(Float, nullable=True)
    end_pos_y = Column(Float, nullable=True)

    # ¡¡NUEVAS COLUMNAS!!
    movement_start_time = Column(DateTime, nullable=True)
    estimated_arrival_time = Column(DateTime, nullable=True)
    
    speed = Column(Float, default=100.0) # Velocidad base de la nave (unidades/segundo)
    
    # --- Nuevos Atributos de Estadísticas Base ---
    cargo_capacity = Column(Integer, default=1000)
    shield_points = Column(Integer, default=100)
    hull_points = Column(Integer, default=500)
    extractor_level = Column(Integer, default=1)
    weapon_slots = Column(Integer, default=2)
    crew_slots = Column(Integer, default=4)

    # Relación
    owner = relationship("User", back_populates="ship")