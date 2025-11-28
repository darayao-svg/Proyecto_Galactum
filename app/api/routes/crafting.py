# app/api/routes/crafting.py
# app/api/routes/crafting.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any, Dict

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.models.crafting import Recipe # Importamos el modelo de recetas
from app.services import crafting_service, job_queue_service, inventory_service # Mantenemos los otros servicios
from app.schemas.crafting import CraftRequest, CraftResponse, RecipeResponse, JobResponse, EquipmentResponse
from datetime import datetime, timezone

router = APIRouter(tags=["Crafting"])

@router.post("/api/v1/craft/item", response_model=CraftResponse, summary="Craftear un item")
def craft_item_endpoint(
    peticion: CraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Craftea un ítem basado en una receta, consumiendo los recursos necesarios.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    try:
        # Usamos la nueva función del servicio
        resultado = crafting_service.craftear_recurso(
            db, current_user.jugador.id, peticion.recipe_id
        )
        db.commit()
        # Adaptamos la respuesta al schema CraftResponse
        produced_item = resultado['produced'][0] if resultado['produced'] else {}
        return CraftResponse(
            status="success", 
            message=f"Crafteado {produced_item.get('quantity', 0)}x {produced_item.get('id', 'N/A')}",
            crafted_item_id=produced_item.get('id', 'N/A'),
            crafted_quantity=produced_item.get('quantity', 0)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/api/v1/factory/recipes", response_model=List[RecipeResponse])
def get_factory_recipes(db: Session = Depends(get_db)):
    """
    Obtiene todas las recetas disponibles para la fábrica.
    """
    return db.query(Recipe).filter(Recipe.type == 'fabrica').all()

@router.get("/api/v1/armory/blueprints", response_model=List[RecipeResponse])
def get_armory_blueprints(db: Session = Depends(get_db)):
    """
    Obtiene todos los planos disponibles para la armería.
    """
    return db.query(Recipe).filter(Recipe.type == 'armeria').all()

@router.post("/api/v1/craft/{recipe_or_blueprint_id}", response_model=JobResponse)
def start_crafting_job(
    recipe_or_blueprint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inicia un nuevo trabajo de crafteo y lo añade a la cola.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    try:
        job = job_queue_service.iniciar_trabajo_crafteo(db, current_user.jugador.id, recipe_or_blueprint_id)
        db.commit()
        return {"status": "success", "job_id": str(job.id), "completion_time": job.completion_time}
    except PermissionError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/api/v1/crafting/queue", response_model=List[Dict[str, Any]])
def get_crafting_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la cola de trabajos de crafteo del jugador, incluyendo el tiempo restante.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    jobs = job_queue_service.obtener_jobs(db, current_user.jugador.id, tipo='crafting')
    
    now = datetime.now(timezone.utc)
    queue_response = []
    for job in jobs:
        remaining_time = (job.completion_time - now).total_seconds()
        queue_response.append({
            "job_id": job.id,
            "item_id": job.related_id,
            "completion_time": job.completion_time,
            "remaining_seconds": max(0, int(remaining_time))
        })
    return queue_response

@router.get("/api/v1/player/equipment", response_model=EquipmentResponse)
def get_player_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el equipamiento actual del jugador.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    equipment = inventory_service.obtener_equipo(db, current_user.jugador.id)
    return {"data": equipment}