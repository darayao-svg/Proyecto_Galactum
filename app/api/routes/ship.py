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

# --- ¡NUEVAS IMPORTACIONES! ---
# 1. Importamos el servicio que contiene la lógica
from app.services import ship as ship_service
# 2. Importamos el modelo de la nave para la consulta
from app.models.ship import Ship
# 3. Importamos el schema de posición que necesita el servicio
from app.schemas.ship import Position

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
    
    # --- ¡LÓGICA REAL (YA NO SON DATOS FALSOS)! ---
    
    try:
        # 1. Llamamos a la función del servicio que ya probaste
        # Le pasamos la BD, el ID del usuario del token, y la posición objetivo
        real_data = ship_service.start_player_move(
            db=db,
            user_id=current_user.id,
            target_pos=move_request.targetPosition
        )
        
        # 2. Devolvemos la respuesta exitosa
        return {
            "status": "success",
            "message": "Movement initiated.",
            "data": real_data # Usamos los datos reales devueltos por el servicio
        }
        
    except Exception as e:
        # 3. Si el servicio falla (ej. "Ship not found"), capturamos 
        # la excepción y devolvemos un error HTTP claro.
        raise HTTPException(
            status_code=400, # 400 = Bad Request (o 404 Not Found)
            detail=str(e) # Esto mostrará el mensaje de error, ej: "Ship not found..."
        )
