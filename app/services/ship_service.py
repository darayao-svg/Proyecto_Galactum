# app/services/ship_service.py
from sqlalchemy.orm import Session, joinedload
from app.models.ship import Ship
from app.models.user import User
from app.schemas.ship import ShipStatus, Position, ShipMoveResponseData
import math
import random # <-- ¡CORRECCIÓN! Importamos el módulo 'random'
from datetime import datetime, timezone, timedelta

# Límites del mapa definidos como constantes para fácil mantenimiento
MAP_MIN_COORDINATE = -10000
MAP_MAX_COORDINATE = 10000

def get_all_ships(db: Session):
    """
    Obtiene el estado de todas las naves para el mapa.
    """
    # Usamos joinedload para cargar las relaciones en una sola consulta y evitar el problema N+1
    ships = db.query(Ship).options(
        joinedload(Ship.owner).joinedload(User.jugador)
    ).all()

    result = []
    for ship in ships:
        # Accedemos a la relación ya cargada, sin hacer nuevas consultas
        nickname = "unknown"
        if ship.owner and ship.owner.jugador:
            nickname = ship.owner.jugador.nickname

        current_pos = Position(x=ship.current_pos_x, y=ship.current_pos_y)  # type: ignore
        start_pos = Position(x=ship.start_pos_x, y=ship.start_pos_y) if ship.start_pos_x is not None and ship.start_pos_y is not None else None  # type: ignore
        end_pos = Position(x=ship.end_pos_x, y=ship.end_pos_y) if ship.end_pos_x is not None and ship.end_pos_y is not None else None  # type: ignore
        result.append(
            ShipStatus(
                username=nickname,
                isMoving=ship.is_moving,  # type: ignore
                currentPosition=current_pos,
                startPosition=start_pos,
                endPosition=end_pos
            )
        )
    return result

def start_player_move(
    db: Session, 
    user_id: str,
    target_pos: Position
) -> ShipMoveResponseData:
    """
    Inicia el movimiento de la nave de un jugador y actualiza la base de datos.
    """
    
    # 1. Encontrar la nave del jugador actual
    ship = db.query(Ship).filter(Ship.owner_id == user_id).first()
    
    if not ship:
        raise Exception("Ship not found for the current user")
        
    # 2. Definir variables de inicio del movimiento
    start_time = datetime.now(timezone.utc)
    start_pos = Position(x=ship.current_pos_x, y=ship.current_pos_y)  # type: ignore
    
    # 3. Calcular distancia y duración del viaje
    distance = math.sqrt(
        (target_pos.x - start_pos.x) ** 2 + 
        (target_pos.y - start_pos.y) ** 2
    )
    
    if distance == 0:
        raise Exception("Already at target position or invalid distance")

    duration_seconds = distance / ship.speed  # type: ignore
    
    # 4. Calcular la hora estimada de llegada (ETA)
    eta = start_time + timedelta(seconds=duration_seconds)  # type: ignore

    # 5. Actualizar todas las columnas de la nave en la BD
    ship.is_moving = True  # type: ignore
    ship.start_pos_x = start_pos.x  # type: ignore
    ship.start_pos_y = start_pos.y  # type: ignore
    ship.end_pos_x = target_pos.x  # type: ignore
    ship.end_pos_y = target_pos.y  # type: ignore
    ship.movement_start_time = start_time  # type: ignore
    ship.estimated_arrival_time = eta  # type: ignore
    
    db.commit()
    db.refresh(ship)

    # 6. Preparar y devolver los datos para la respuesta de la API
    return ShipMoveResponseData(
        endPosition=target_pos,
        estimatedArrivalTime=eta
    )

def create_initial_ship(db: Session, user_id: "uuid.UUID") -> Ship:
    """
    Crea y registra una nueva nave para un usuario recién registrado.
    Esta función se llama durante el proceso de registro de usuario.

    Args:
        db (Session): La sesión de base de datos activa.
        user_id (uuid.UUID): El ID del usuario propietario de la nave.

    Returns:
        Ship: La instancia del modelo Ship recién creada.
    """
    # 1. Generar coordenadas aleatorias para la posición inicial
    initial_pos_x = float(random.randint(MAP_MIN_COORDINATE, MAP_MAX_COORDINATE))
    initial_pos_y = float(random.randint(MAP_MIN_COORDINATE, MAP_MAX_COORDINATE))

    # 2. Crear la instancia del modelo Ship con los valores iniciales
    new_ship = Ship(
        owner_id=user_id,
        is_moving=False,
        current_pos_x=initial_pos_x,
        current_pos_y=initial_pos_y,
        # Asignamos la posición inicial también a start_pos para consistencia
        start_pos_x=initial_pos_x,
        start_pos_y=initial_pos_y,
        # El resto de campos (end_pos, speed, etc.) se dejan en su valor por defecto.
    )

    # 3. Añadir la nueva nave a la sesión de la base de datos.
    # El 'commit' se debe manejar en el servicio que orquesta la transacción (ej. auth_service).
    db.add(new_ship)
    return new_ship