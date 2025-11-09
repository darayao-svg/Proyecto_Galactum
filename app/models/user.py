# app/models/user.py
from sqlalchemy import Column, String, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relaciones
    jugador = relationship("Jugador", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ship = relationship("Ship", back_populates="owner", uselist=False, cascade="all, delete-orphan")
