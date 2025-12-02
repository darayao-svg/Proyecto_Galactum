from sqlalchemy.orm import Session
from typing import List, cast
from datetime import datetime
import random

from app.models.asteroid import Asteroid
from app.schemas.asteroid import AsteroidStatus, Position

# Configuración del mapa (mismo que en el script de seed)
MAP_LIMIT = 10000

def recover_asteroids(db: Session):
    """
    Revisa si hay asteroides 'muertos' cuyo tiempo de espera ya pasó.
    Si encuentra alguno, lo revive, lo rellena y lo TELETRANSPORTA.
    """
    now = datetime.utcnow()
    
    # Buscar asteroides inactivos que ya cumplieron su tiempo de respawn
    to_respawn = db.query(Asteroid).filter(
        Asteroid.is_active == False,
        Asteroid.reaparecer_en <= now
    ).all()
    
    if not to_respawn:
        return

    for ast in to_respawn:
        # 1. Nueva posición aleatoria
        new_x = random.uniform(-MAP_LIMIT, MAP_LIMIT)
        new_y = random.uniform(-MAP_LIMIT, MAP_LIMIT)
        
        # 2. Actualizar datos en la BD
        ast.position_x = new_x
        ast.position_y = new_y
        ast.is_active = True
        ast.reaparecer_en = None
        
        # 3. Rellenar mineral al máximo original
        ast.cantidad_restante = ast.cantidad_maxima 
        
    db.commit()

def get_all_asteroids(db: Session) -> List[AsteroidStatus]:
    """
    Obtiene todos los asteroides ACTIVOS del mapa.
    También ejecuta el mantenimiento de respawn.
    """
    # 1. Ejecutar lógica de respawn antes de consultar
    recover_asteroids(db)

    # 2. Consultar solo los activos
    asteroids_from_db = db.query(Asteroid).filter(Asteroid.is_active == True).all()
    
    asteroids_list = []
    for ast in asteroids_from_db:
        # Mapeo manual seguro con cast
        asteroids_list.append(AsteroidStatus(
            asteroid=cast(str, ast.asteroid),
            position=Position(
                x=cast(float, ast.position_x), 
                y=cast(float, ast.position_y)
            ),
            resourceType=cast(str, ast.resource_type),
            cantidad_restante=cast(int, ast.cantidad_restante),
            cantidad_maxima=cast(int, ast.cantidad_maxima)
        ))
    
    return asteroids_list