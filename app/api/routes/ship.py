# En app/api/routes/ship.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime

# --- ¡IMPORTACIONES CORREGIDAS! ---
# Estas son las rutas correctas, copiadas de tu 'users.py'
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User  # Para el tipo de 'current_user'
from app.schemas.ship import ShipMoveRequest, ShipMoveResponse # Importamos los schemas

# (En el paso 3 importaremos 'services' aquí)

router = APIRouter(prefix="/api/v1/player", tags=["Player"])

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
    
    # ---------------------------------------------------------------
    # ¡AQUÍ IRÁ LA LÓGICA EN EL PASO 4!
    # Por ahora, solo devolvemos datos falsos para probar
    # ---------------------------------------------------------------
    
    # Datos falsos temporales
    fake_eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    
    return {
        "status": "success",
        "message": "Movement initiated.",
        "data": {
            "endPosition": move_request.targetPosition.model_dump(),
            "estimatedArrivalTime": fake_eta
        }
    }