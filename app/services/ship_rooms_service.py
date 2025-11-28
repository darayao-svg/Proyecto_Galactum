from sqlalchemy.orm import Session
from app.models.ship_rooms import ShipRoom
from app.models.jugador import Jugador
from app.models.user import User # Importamos el modelo User para buscar por user_id
from app.models.config_room_costs import ConfigRoomCost
from app.services import recursos_service
from app.services import misiones_service
import json

# Lista de salas iniciales
SALAS_INICIALES = [
    {"room_id": "Fabrica", "level": 1},
    {"room_id": "Armeria", "level": 1}
]

def crear_salas_iniciales(db: Session, user_id: "uuid.UUID"):
    """
    Crea las salas iniciales para un jugador.
    Corrección: Ahora recibe user_id (UUID) y busca el jugador correspondiente.
    """
    # Buscamos el perfil del jugador a través de la relación con el usuario.
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if not user or not user.jugador:
        # Esto no debería ocurrir en un flujo de registro normal, pero es una validación segura.
        raise Exception("No se encontró el perfil de jugador para el usuario al crear salas.")

    player_id = user.jugador.id # Obtenemos el ID numérico del jugador.

    for sala in SALAS_INICIALES:
        db_room = ShipRoom(
            player_id=player_id,
            room_id=sala["room_id"],
            level=sala["level"]
        )
        db.add(db_room)
    # El commit se maneja en el servicio que orquesta la transacción (ej. auth_service).

def obtener_info_salas(db: Session, player_id: int):
    """
    Obtiene la información de las salas de un jugador, incluyendo el costo de la próxima mejora.
    Recibe el ID numérico del jugador directamente.
    """
    player_rooms = db.query(ShipRoom).filter(ShipRoom.player_id == player_id).all()
 
    response_data = []
    for room in player_rooms:
        # 2. Para cada sala, calculamos cuál sería el siguiente nivel.
        next_level = room.level + 1
        
        # 3. Buscamos en la tabla de configuración el costo para alcanzar ese siguiente nivel.
        cost_config = db.query(ConfigRoomCost).filter(
            ConfigRoomCost.room_id == room.room_id,
            ConfigRoomCost.target_level == next_level
        ).first()
        
        # 4. Preparamos el objeto de respuesta para esta sala.
        room_info = {
            "roomId": room.room_id,
            "level": room.level,
            # Si encontramos un costo de mejora, lo incluimos. Si no (porque es el nivel máximo), será null.
            "nextLevelCost": json.loads(cost_config.cost_data) if cost_config else None # type: ignore
        }
        response_data.append(room_info)
        
    # 5. Devolvemos la lista completa de salas con su información.
    return response_data


def upgrade_room(db: Session, player_id: int, room_id: str):
    """
    Lógica de negocio para mejorar una sala. Es una operación transaccional.
    Recibe el ID numérico del jugador directamente.
    """
    # 1. Buscar la sala actual del jugador.
    room_to_upgrade = db.query(ShipRoom).filter(
        ShipRoom.player_id == player_id,
        ShipRoom.room_id == room_id
    ).with_for_update().first()

    if not room_to_upgrade:
        raise Exception(f"Sala '{room_id}' no encontrada para este jugador.")

    current_level = room_to_upgrade.level
    target_level = current_level + 1

    # 2. Buscar el costo para el siguiente nivel
    cost_config = db.query(ConfigRoomCost).filter(
        ConfigRoomCost.room_id == room_id,
        ConfigRoomCost.target_level == target_level
    ).first()

    if not cost_config:
        raise Exception(f"No hay un costo de mejora definido para '{room_id}' a nivel {target_level}.")

    costo_lista = json.loads(cost_config.cost_data) # type: ignore

    # 3. Llamar al servicio de recursos para consumir el costo (usando el ID numérico del jugador)
    # Si no hay suficientes recursos, lanzará una excepción y la transacción se revertirá.
    recursos_service.verificar_y_consumir_recursos(db, player_id, costo_lista) # type: ignore

    # 4. Si tiene éxito, actualizar el nivel de la sala
    room_to_upgrade.level = target_level # type: ignore

    # 5. Hook de Misión: Notificar al servicio de misiones sobre la mejora
    misiones_service.actualizar_progreso_mision(db, player_id, tipo_objetivo='upgrade_room', objetivo_id=room_id) # type: ignore

    return room_to_upgrade