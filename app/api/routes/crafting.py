# app/api/routes/crafting.py
# app/api/routes/crafting.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services import crafting_service, job_queue_service, inventory_service
from app.schemas.crafting import CraftRequest, CraftResponse, RecipeResponse, JobResponse, EquipmentResponse

router = APIRouter(tags=["Crafting"])

@router.post("/api/v1/craft/item", response_model=CraftResponse, summary="Legacy Crafting Endpoint")
def craft_item_endpoint(
    peticion: CraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Craftea un ítem basado en una receta, consumiendo los recursos necesarios (legacy).
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    try:
        resultado = crafting_service.craft_item(
            db, current_user.jugador.id, peticion.recipe_id, getattr(peticion, 'quantity', 1)
        )
        db.commit()
        return CraftResponse(status="success", message=f"Crafteado {resultado['crafted_quantity']}x {resultado['crafted_item_id']}", **resultado)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/api/v1/factory/recipes", response_model=List[RecipeResponse])
def get_factory_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las recetas disponibles para la fábrica.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return crafting_service.obtener_recetas(db=db, tipo='fabrica')

@router.get("/api/v1/armory/blueprints", response_model=List[RecipeResponse])
def get_armory_blueprints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los planos disponibles para la armería.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    return crafting_service.obtener_recetas(db=db, tipo='armeria')

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
        job = crafting_service.iniciar_trabajo_crafteo(db, current_user.jugador.id, recipe_or_blueprint_id)
        db.commit()
        return {"status": "success", "job_id": job.id, "completion_time": job.completion_time}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/api/v1/crafting/queue", response_model=List[JobResponse])
def get_crafting_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la cola de trabajos de crafteo del jugador.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    jobs = job_queue_service.obtener_jobs(db, current_user.jugador.id, tipo='crafting')
    return [{"status": "pending", "job_id": job.id, "completion_time": job.completion_time} for job in jobs]

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