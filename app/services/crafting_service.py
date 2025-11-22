# app/services/crafting_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Es necesario importar los modelos de la base de datos.
# Asumo que tienes un modelo 'Recipe' en 'app/models/crafting.py'
# y un modelo 'Job' en 'app/models/job.py'
from app.models.crafting import Recipe
from app.models.job import Job

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

# TODO: Implementar la función craft_item que se usa en el endpoint legacy.