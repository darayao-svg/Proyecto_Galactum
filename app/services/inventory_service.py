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

def agregar_equipo(db: Session, player_id: int, item_id: str, quantity: int):
    """
    Añade una cantidad de un ítem de equipamiento al inventario de un jugador.
    Maneja la lógica de INSERT/UPDATE.
    """
    player_item = db.query(PlayerEquipment).filter(
        PlayerEquipment.player_id == player_id,
        PlayerEquipment.item_id == item_id
    ).with_for_update().first()

    if player_item:
        player_item.quantity += quantity # type: ignore
    else:
        new_player_item = PlayerEquipment(
            player_id=player_id,
            item_id=item_id,
            quantity=quantity
        )
        db.add(new_player_item)