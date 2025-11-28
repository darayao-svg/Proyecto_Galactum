from sqlalchemy.orm import Session
from app.models.ship_rooms import ShipRoom
from app.models.jugador import Jugador # <-- ¡CORRECCIÓN! Usamos el modelo y archivo correctos.
from app.models.config_room_costs import ConfigRoomCost
from app.services import recursos_service
from app.services import misiones_service
import json
from datetime import datetime, timedelta, timezone
from typing import cast

# Lista de salas iniciales
SALAS_INICIALES = [
    {"room_id": "Fabrica", "level": 1},
    {"room_id": "Armeria", "level": 1}
]

# Mock de datos estáticos para las salas. En un sistema real, esto estaría en una tabla `config_rooms`.
CONFIG_ROOM_DETAILS = {
    "Fabrica": {"name": "Fábrica", "description": "Produce unidades y equipamiento básico."},
    "Armeria": {"name": "Armería", "description": "Diseña y construye armamento avanzado."}
}

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
    # --- CORRECCIÓN ---
    # 1. El 'player_id' que recibimos es el UUID del usuario. Necesitamos el ID numérico del jugador.
    # Buscamos en la tabla 'players' (o 'jugadores') usando el user_id (UUID).
    player_profile = db.query(Jugador).filter(Jugador.user_id == player_id).first()

    if not player_profile:
        # Si por alguna razón no hay un perfil de jugador para este usuario, devolvemos una lista vacía.
        return []

    # 2. Ahora usamos el ID numérico del jugador (player_profile.id) para buscar sus salas.
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
            "room_id": room.room_id,
            "name": CONFIG_ROOM_DETAILS.get(cast(str, room.room_id), {}).get("name", room.room_id),
            "level": room.level,
            "status": room.status, # Añadimos el estado actual de la sala
            # Si encontramos un costo de mejora, lo incluimos. Si no (porque es el nivel máximo), será null.
            "next_level_desc": f"Mejora la eficiencia y desbloquea nuevas recetas de nivel {next_level}." if cost_config else "Nivel máximo alcanzado.",
            "upgrade_cost": json.loads(cost_config.cost_data) if cost_config else [], # type: ignore
            "completion_time": room.upgrade_finish_time # Añadimos el tiempo de finalización si está mejorando
        }
        response_data.append(room_info)
        
    # 5. Devolvemos la lista completa de salas con su información.
    return response_data


def upgrade_room(db: Session, player_id: int, room_id: str):
    """
    Lógica de negocio para INICIAR la mejora asíncrona de una sala.
    El commit/rollback debe ser manejado por el endpoint que la llama.
    """
    # --- CORRECCIÓN ---
    # Al igual que en la función anterior, necesitamos el ID numérico del jugador.
    player_profile = db.query(Jugador).filter(Jugador.user_id == player_id).first()

    if not player_profile:
        raise Exception("Perfil de jugador no encontrado para este usuario.")

    # 1. Buscar la sala actual del jugador usando el ID numérico.
    room_to_upgrade = db.query(ShipRoom).filter(
        ShipRoom.player_id == player_profile.id,
        ShipRoom.room_id == room_id
    ).with_for_update().first()

    if not room_to_upgrade:
        raise Exception(f"Sala '{room_id}' no encontrada para este jugador.")

    # 1. Validación de Prerrequisitos Adicionales
    if room_to_upgrade.status == 'Upgrading': # Asumimos que la columna 'status' existe
        raise Exception(f"La sala '{room_id}' ya se está mejorando.")

    current_level = room_to_upgrade.level
    target_level = current_level + 1

    # 2. Buscar el costo para el siguiente nivel
    cost_config = db.query(ConfigRoomCost).filter(
        ConfigRoomCost.room_id == room_id,
        ConfigRoomCost.target_level == target_level
    ).first()

    if not cost_config:
        raise Exception(f"No hay un costo de mejora definido para '{room_id}' a nivel {target_level}.")

    # 3. Cálculo de Tiempo y Consumo de Recursos
    costo_lista = json.loads(cost_config.cost_data) # type: ignore
    # Asumimos que el modelo ConfigRoomCost tiene una columna 'duration_seconds'
    duration_seconds = cost_config.duration_seconds if hasattr(cost_config, 'duration_seconds') else 3600 # Default a 1 hora

    # Si no hay suficientes recursos, lanzará una excepción y la transacción se revertirá.
    recursos_service.verificar_y_consumir_recursos(db, player_profile.id, costo_lista) # type: ignore

    # 4. Actualizar la sala para iniciar la mejora
    now = datetime.now(timezone.utc)
    completion_time = now + timedelta(seconds=duration_seconds)
    
    room_to_upgrade.status = 'Upgrading' # type: ignore
    room_to_upgrade.upgrade_finish_time = completion_time # type: ignore
    # NO actualizamos el nivel todavía.

    # 5. Hook de Misión: Notificar al servicio de misiones sobre la mejora
    misiones_service.actualizar_progreso_mision(db, player_profile.id, tipo_objetivo='upgrade_room', objetivo_id=room_id) # type: ignore

    # 6. Devolver la respuesta esperada
    return {
        "status": "upgrade_started",
        "room_id": room_id,
        "completion_time": completion_time
    }

def check_and_complete_upgrades(db: Session):
    """
    Verifica y finaliza las mejoras de salas que han terminado.
    Esta función debe ser llamada periódicamente por un trabajo programado (cron job).
    """
    now = datetime.now(timezone.utc)
    
    # Buscar todas las salas que están mejorándose y cuyo tiempo ha finalizado
    finished_upgrades = db.query(ShipRoom).filter(
        ShipRoom.status == 'Upgrading', # type: ignore
        ShipRoom.upgrade_finish_time <= now # type: ignore
    ).all()

    for room in finished_upgrades:
        room.level += 1 # type: ignore
        room.status = 'Ready' # type: ignore
        room.upgrade_finish_time = None # type: ignore

    if finished_upgrades:
        db.commit()
    
    return len(finished_upgrades)