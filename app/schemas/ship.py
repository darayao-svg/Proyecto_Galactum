from pydantic import BaseModel
from typing import Optional

class Position(BaseModel):
    x: float
    y: float

class ShipStatus(BaseModel):
    username: str
    isMoving: bool
    currentPosition: Position
    startPosition: Optional[Position] = None
    endPosition: Optional[Position] = None

class ShipsResponse(BaseModel):
    status: str = "success"
    data: list[ShipStatus]