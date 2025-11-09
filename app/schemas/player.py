# app/schemas/player.py
from pydantic import BaseModel

class InventoryItem(BaseModel):
    resource_id: str
    quantity: int

    class Config:
        from_attributes = True

class RoomStatus(BaseModel):
    room_id: str
    level: int