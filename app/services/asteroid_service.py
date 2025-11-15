# app/services/asteroid_service.py
from sqlalchemy.orm import Session
from app.schemas.asteroid import AsteroidStatus, Position

def get_all_asteroids(db: Session):
    """
    Obtiene la información de todos los asteroides (mock).
    """
    # Datos de ejemplo, en el futuro esto vendría de la base de datos
    mock_asteroids = [
        AsteroidStatus(
            asteroidId="AST-001",
            position=Position(x=150.0, y=250.0),
            resourceType="Roderitium"
        )
    ]
    return mock_asteroids