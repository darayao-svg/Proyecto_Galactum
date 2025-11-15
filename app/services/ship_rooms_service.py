from sqlalchemy.orm import Session
from app.models.ship_rooms import ShipRoom
from app.models.config_room_costs import ConfigRoomCost
from app.services import recursos_service
from app.services import misiones_service
import json

# Lista de salas iniciales
SALAS_INICIALES = [
    {"room_id": "Fabrica", "level": 1},
    {"room_id": "Armeria", "level": 1}
]

def crear_salas_iniciales(db: Session, player_id: int):
    for sala in SALAS_INICIALES:
        db_room = ShipRoom(
            player_id=player_id,
            room_id=sala["room_id"],
            level=sala["level"]
        )
        db.add(db_room)
    # Nota: No hacemos commit aquí. El servicio que nos llama (auth_service)
    # se encargará del commit de la transacción completa.

def obtener_configuracion_salas(db: Session, player_id: int):
    """
    Obtiene la configuración de todas las salas de la nave de un jugador.
    Responde a la Tarea 3.2 (GET /player/config).
    """
    return db.query(ShipRoom).filter(ShipRoom.player_id == player_id).all()

def upgrade_room(db: Session, player_id: int, room_id: str):
    """
    Lógica de negocio para mejorar una sala. Es una operación transaccional.
    El commit/rollback debe ser manejado por el endpoint que la llama.
    """
    # 1. Buscar la sala actual del jugador
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

    # 3. Llamar al servicio de recursos para consumir el costo
    # Si no hay suficientes recursos, lanzará una excepción y la transacción se revertirá.
    recursos_service.verificar_y_consumir_recursos(db, player_id, costo_lista)

    # 4. Si tiene éxito, actualizar el nivel de la sala
    room_to_upgrade.level = target_level # type: ignore

    # 5. Hook de Misión: Notificar al servicio de misiones sobre la mejora
    misiones_service.actualizar_progreso_mision(db, player_id, tipo_objetivo='upgrade_room', objetivo_id=room_id)

    return room_to_upgrade