from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

# (Para el nuevo endpoint de 'iniciar movimiento')

# 1. Lo que el jugador ENVÍA (Request Body)
class ShipMoveRequest(BaseModel):
    targetPosition: Position

# 2. Los datos que la API DEVUELVE (anidado en la respuesta)
class ShipMoveResponseData(BaseModel):
    endPosition: Position
    estimatedArrivalTime: datetime

# 3. La respuesta COMPLETA de la API
class ShipMoveResponse(BaseModel):
    status: str = "success"
    message: str = "Movement initiated."
    data: ShipMoveResponseData