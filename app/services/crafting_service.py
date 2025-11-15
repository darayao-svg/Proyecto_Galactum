# app/services/crafting_service.py
from sqlalchemy.orm import Session
import json

from app.models.config_craft_recipes import ConfigCraftRecipe
from app.models.player_equipment import PlayerEquipment
from app.models.ship_rooms import ShipRoom
from app.services import recursos_service
from app.services import misiones_service

def craft_item(db: Session, player_id: int, recipe_id: str, quantity: int = 1):
    """
    Lógica de negocio para craftear un ítem. Es una operación transaccional.
    El commit/rollback debe ser manejado por el endpoint que la llama.
    """
    # 1. Buscar la receta
    recipe = db.query(ConfigCraftRecipe).filter(ConfigCraftRecipe.recipe_id == recipe_id).first()
    if not recipe:
        raise Exception(f"Receta '{recipe_id}' no encontrada.")

    # 2. Verificar prerrequisito de sala
    required_room_id = recipe.required_room_id
    required_room_level = recipe.required_room_level

    player_room = db.query(ShipRoom).filter(
        ShipRoom.player_id == player_id,
        ShipRoom.room_id == required_room_id
    ).first()

    if not player_room or player_room.level < required_room_level:  # type: ignore
        raise Exception(f"Se requiere {required_room_id} Nivel {required_room_level} para esta receta.")

    # 3. Cargar y calcular el costo total
    costo_unitario = json.loads(recipe.resource_cost_json)  # type: ignore
    costo_total = [{"id": item["id"], "quantity": item["quantity"] * quantity} for item in costo_unitario]

    # 4. Llamar al servicio de recursos para consumir el costo
    recursos_service.verificar_y_consumir_recursos(db, player_id, costo_total)

    # 5. Si tiene éxito, añadir el ítem al inventario de equipo del jugador
    output_item_id = recipe.output_item_id
    player_item = db.query(PlayerEquipment).filter(
        PlayerEquipment.player_id == player_id,
        PlayerEquipment.item_id == output_item_id
    ).with_for_update().first()

    if player_item:
        player_item.quantity += quantity  # type: ignore
    else:
        player_item = PlayerEquipment(
            player_id=player_id,
            item_id=output_item_id,
            quantity=quantity
        )
        db.add(player_item)

    # 6. Hook de Misión: Notificar al servicio de misiones sobre el crafteo
    misiones_service.actualizar_progreso_mision(
        db, player_id, tipo_objetivo='craft_item', objetivo_id=recipe_id, cantidad=quantity
    )

    # El commit se maneja en el endpoint
    return {
        "crafted_item_id": output_item_id,
        "crafted_quantity": quantity
    }