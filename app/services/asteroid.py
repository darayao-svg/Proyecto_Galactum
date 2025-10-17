from sqlalchemy.orm import Session
from app.models.asteroid import Asteroid
from app.schemas.asteroid import AsteroidStatus, Position

def get_all_asteroids(db: Session):
    asteroids = db.query(Asteroid).all()
    result = []
    for ast in asteroids:
        result.append(
            AsteroidStatus(
                asteroidId=ast.asteroid_id,
                position=Position(x=ast.pos_x, y=ast.pos_y),
                resourceType=ast.resource_type
            )
        )
    return result