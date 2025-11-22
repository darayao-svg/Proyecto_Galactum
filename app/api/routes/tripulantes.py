from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services import tripulantes_service
from app.schemas.crew import CrewAssignRequest, CrewSpecializeRequest

router = APIRouter(
    prefix="/api/v1",
    tags=["crew"],
)

@router.get("/player/crew")
def get_crew(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    player_id = current_user.jugador.id
    return tripulantes_service.obtener_tripulantes(db, player_id)

@router.post("/crew/{crew_id}/assign")
def assign_crew(
    crew_id: int,
    body: CrewAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    player_id = current_user.jugador.id
    return tripulantes_service.asignar_tripulante(db, player_id, crew_id, body.slot_id)

@router.post("/crew/{crew_id}/levelup")
def levelup_crew(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    player_id = current_user.jugador.id
    return tripulantes_service.subir_nivel_tripulante(db, player_id, crew_id)

@router.post("/crew/{crew_id}/specialize")
def specialize_crew(
    crew_id: int,
    body: CrewSpecializeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    player_id = current_user.jugador.id
    return tripulantes_service.especializar_tripulante(db, player_id, crew_id, body.specialization_id)
