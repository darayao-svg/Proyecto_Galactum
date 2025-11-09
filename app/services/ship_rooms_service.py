from sqlalchemy.orm import Session
from app.models.ship_rooms import ShipRoom

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