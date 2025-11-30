# app/schemas/player.py
from pydantic import BaseModel
from typing import List

class InventoryItem(BaseModel):
    resource_id: int
    quantity: int

    class Config:
        from_attributes = True

class RoomStatus(BaseModel):
    room_id: str
    level: int

class InventoryResponse(BaseModel):
    recursos: List[InventoryItem]