# app/schemas/server.py
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class ServerBase(BaseModel):
    name: str
    region: str

class ServerCreate(ServerBase):
    """Payload para crear servidor."""
    pass

class ServerUpdate(BaseModel):
    """Payload para actualizar servidor (parcial)."""
    name: Optional[str] = None
    region: Optional[str] = None

class ServerOut(ServerBase):
    """Respuesta pública de servidor."""
    id: UUID
    owner_id: UUID

    # Permite construir el esquema desde instancias de SQLAlchemy
    model_config = {"from_attributes": True}
