# En app/api/routes/ship.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.ship import ShipMoveRequest, ShipMoveResponse
# --- ¡IMPORTACIÓN CORREGIDA! ---
# Apuntamos al nuevo servicio en la carpeta de servicios
from app.services import ship_service

# (En el paso 3 importaremos 'services' aquí)

router = APIRouter(prefix="/api/v1/player", tags=["player"])

@router.post(
    "/move", 
    response_model=ShipMoveResponse, # Usamos el schema importado
    summary="Iniciar Movimiento de la Nave"
)
async def move_ship(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Usamos el modelo importado
    move_request: ShipMoveRequest # Usamos el schema importado
):
    """
    Establece un nuevo punto de destino para la nave del jugador.
    """
    try:
        # 1. Llamamos a la función del nuevo servicio
        # Le pasamos la BD, el ID del usuario y la posición objetivo
        real_data = ship_service.start_player_move(
            db=db,
            user_id=current_user.id,
            target_pos=move_request.targetPosition
        )
        
        return {
            "status": "success",
            "message": "Movement initiated.",
            "data": real_data # Usamos los datos reales devueltos por el servicio
        }
        
    except Exception as e:
        # 2. Si el servicio falla, capturamos la excepción y devolvemos un error HTTP.
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
