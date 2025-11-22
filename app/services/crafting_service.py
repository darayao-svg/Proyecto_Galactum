# app/services/crafting_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Es necesario importar los modelos de la base de datos.
# Asumo que tienes un modelo 'Recipe' en 'app/models/crafting.py'
# y un modelo 'Job' en 'app/models/job.py'
from app.models.crafting import Recipe
from app.models.job import Job
from app.services import recursos_service, inventory_service
import json


def obtener_recetas(db: Session, tipo: str):
    """
    Obtiene todas las recetas de un tipo específico ('fabrica' o 'armeria')
    desde la base de datos.
    """
    recetas_db = db.query(Recipe).filter(Recipe.type == tipo).all()
    return recetas_db

def iniciar_trabajo_crafteo(db: Session, player_id: int, recipe_id: str):
    """
    Inicia un nuevo trabajo de crafteo.
    TODO: Implementar la lógica de consumo de recursos.
    """
    receta = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not receta:
        raise Exception("Receta no encontrada")

    # Lógica de ejemplo: el trabajo dura 5 minutos
    tiempo_finalizacion = datetime.utcnow() + timedelta(minutes=5)

    nuevo_trabajo = Job(
        player_id=player_id,
        job_type='crafting',
        related_id=recipe_id,
        completion_time=tiempo_finalizacion
    )
    db.add(nuevo_trabajo)
    db.flush() # Para obtener el ID del trabajo antes del commit
    return nuevo_trabajo

def craft_item(db: Session, player_id: int, recipe_id: str, quantity: int = 1):
    """
    Lógica de negocio para craftear un ítem (legacy). Es una operación transaccional.
    El commit/rollback debe ser manejado por el endpoint que la llama.
    """
    # 1. Buscar la receta
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise Exception(f"Receta '{recipe_id}' no encontrada.")

    # 2. Cargar y calcular el costo total
    costo_unitario = json.loads(recipe.ingredients) # type: ignore
    costo_total = [{"id": item["item_id"], "quantity": item["quantity"] * quantity} for item in costo_unitario]

    # 3. Llamar al servicio de recursos para consumir el costo
    recursos_service.verificar_y_consumir_recursos(db, player_id, costo_total)

    # 4. Si tiene éxito, añadir el ítem al inventario de equipamiento
    # Asumimos que el 'id' de la receta es el 'item_id' del producto final.
    crafted_item_id = recipe.id # type: ignore
    inventory_service.agregar_equipo(db, player_id, crafted_item_id, quantity) # type: ignore

    # 5. Hook de Misión: Notificar al servicio de misiones sobre la creación
    # (Ajusta 'tipo_objetivo' y 'objetivo_id' según tu modelo de misiones)
    # misiones_service.actualizar_progreso_mision(
    #     db, player_id, tipo_objetivo='craft_item', objetivo_id=crafted_item_id, cantidad=quantity
    # )

    return {
        "crafted_item_id": crafted_item_id,
        "crafted_quantity": quantity
    }