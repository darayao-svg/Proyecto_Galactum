# app/models/ship.py
from sqlalchemy import Column, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base
from app.models.user import User

class Ship(Base):
    __tablename__ = "ships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # --- Relación con el Usuario ---
    # Se asegura que cada nave pertenezca a un único usuario.
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    owner = relationship("User")

    # --- Estado y Posición ---
    # Usamos valores por defecto para la posición inicial de la nave.
    is_moving = Column(Boolean, default=False, nullable=False)
    current_pos_x = Column(Float, default=0.0, nullable=False)
    current_pos_y = Column(Float, default=0.0, nullable=False)
    
    # Estos campos se usarán cuando la nave se esté moviendo.
    start_pos_x = Column(Float, nullable=True)
    start_pos_y = Column(Float, nullable=True)
    
    end_pos_x = Column(Float, nullable=True)
    end_pos_y = Column(Float, nullable=True)