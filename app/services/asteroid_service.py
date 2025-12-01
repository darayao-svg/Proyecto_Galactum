# app/services/asteroid_service.py
from sqlalchemy.orm import Session
from app.schemas.asteroid import AsteroidStatus, Position
from app.models.asteroid import Asteroid
from typing import cast

def get_all_asteroids(db: Session):
    """
    Obtiene la información de todos los asteroides desde la base de datos.
    """
    asteroids_from_db = db.query(Asteroid).all()
    
    asteroids = []
    for asteroid_db in asteroids_from_db:
        asteroids.append(AsteroidStatus(
            asteroid=cast(str, asteroid_db.asteroid),
            position=Position(x=cast(float, asteroid_db.position_x), y=cast(float, asteroid_db.position_y)),
            resourceType=cast(str, asteroid_db.resource_type),
            cantidad_restante=cast(int, asteroid_db.cantidad_restante)
        )
    )
    return asteroids