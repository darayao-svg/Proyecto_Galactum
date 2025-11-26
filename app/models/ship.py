# app/models/ship.py - CORREGIDO
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Column, Float, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class Ship(Base):
    __tablename__ = "ships"
    id = Column(Integer, primary_key=True, index=True)
    # 1. Columna 'id' como UUID con autogeneración en Python
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
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

    # Relación
    owner = relationship("User", back_populates="ship")