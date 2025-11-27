from sqlalchemy.orm import Session
from app.models.ship_rooms import ShipRoom
from app.models.jugador import Jugador # <-- ¡CORRECCIÓN! Usamos el modelo y archivo correctos.
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

def obtener_info_salas(db: Session, player_id: int):
    """
    Obtiene la información de las salas de un jugador, incluyendo el costo de la próxima mejora.
    Esta función reemplaza a la antigua `obtener_configuracion_salas`.
    """
    # --- NUEVA CORRECCIÓN ---
    # El 'player_id' que recibimos desde el endpoint es el ID numérico del jugador (jugador.id).
    # Por lo tanto, debemos buscar en la tabla 'jugadores' usando su clave primaria 'id'.
    player_profile = db.query(Jugador).filter(Jugador.id == player_id).first()

    if not player_profile:
        # Si por alguna razón no hay un perfil de jugador para este usuario, devolvemos una lista vacía.
        return []

    # Ahora usamos el ID numérico del jugador (player_profile.id) para buscar sus salas.
    player_rooms = db.query(ShipRoom).filter(ShipRoom.player_id == player_profile.id).all()
    
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
    El commit/rollback debe ser manejado por el endpoint que la llama.
    """
    # --- NUEVA CORRECCIÓN ---
    # Al igual que en la función anterior, el 'player_id' es el ID numérico.
    player_profile = db.query(Jugador).filter(Jugador.id == player_id).first()

    if not player_profile:
        raise Exception("Perfil de jugador no encontrado para este usuario.")

    # Buscar la sala actual del jugador usando el ID numérico.
    room_to_upgrade = db.query(ShipRoom).filter(
        ShipRoom.player_id == player_profile.id,
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
    recursos_service.verificar_y_consumir_recursos(db, player_profile.id, costo_lista) # type: ignore

    # 4. Si tiene éxito, actualizar el nivel de la sala
    room_to_upgrade.level = target_level # type: ignore

    # 5. Hook de Misión: Notificar al servicio de misiones sobre la mejora
    misiones_service.actualizar_progreso_mision(db, player_profile.id, tipo_objetivo='upgrade_room', objetivo_id=room_id) # type: ignore

    return room_to_upgrade