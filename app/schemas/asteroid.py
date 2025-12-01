from pydantic import BaseModel

class Position(BaseModel):
    x: float
    y: float

class AsteroidStatus(BaseModel):
    asteroid: str
    position: Position
    resourceType: str
    cantidad_restante: int


class AsteroidsResponse(BaseModel):
    status: str = "success"
    data: list[AsteroidStatus]