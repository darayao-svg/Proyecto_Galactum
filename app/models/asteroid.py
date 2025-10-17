from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class Asteroid(Base):
    __tablename__ = "asteroids"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asteroid_id = Column(String, unique=True, nullable=False)
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    resource_type = Column(String, nullable=False)