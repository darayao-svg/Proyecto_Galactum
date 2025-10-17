from pydantic import BaseModel

class Position(BaseModel):
    x: float
    y: float

class AsteroidStatus(BaseModel):
    asteroidId: str
    position: Position
    resourceType: str

class AsteroidsResponse(BaseModel):
    status: str = "success"
    data: list[AsteroidStatus]