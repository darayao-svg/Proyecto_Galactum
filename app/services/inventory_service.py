# app/services/inventory_service.py
from sqlalchemy.orm import Session
from app.models.player_equipment import PlayerEquipment

def obtener_equipo(db: Session, player_id: int):
    """
    Obtiene el equipamiento de un jugador.
    NOTA: Para añadir el 'name', se necesitaría un JOIN con una tabla de ítems.
    """
    equipment = db.query(PlayerEquipment).filter(PlayerEquipment.player_id == player_id).all()
    return [{"item_id": item.item_id, "name": item.item_id, "quantity": item.quantity} for item in equipment]