# app/models/ship.py
from sqlalchemy import Column, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class Ship(Base):
    __tablename__ = "ships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
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