# app/models/ship.py
from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class Ship(Base):
    __tablename__ = "ships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, ForeignKey("users.username"))
    is_moving = Column(Boolean, default=False)
    current_x = Column(Float)
    current_y = Column(Float)
    start_x = Column(Float, nullable=True)
    start_y = Column(Float, nullable=True)
    end_x = Column(Float, nullable=True)
    end_y = Column(Float, nullable=True)