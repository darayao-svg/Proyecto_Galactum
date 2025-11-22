from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.services.auth import get_current_user
from app.models.user import User
from app.db.dependencies import get_db
from app.services import ship_rooms_service
from app.services import recursos_service
from app.schemas.ship_room import ShipRoomOut
from app.schemas.player import InventoryResponse

# Definimos el router para este módulo
router = APIRouter(prefix="/api/v1/player", tags=["player"])

# --- Obtener perfil del jugador ---
@router.get("/profile", name="Get player profile")
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Devuelve la información básica y los recursos del jugador autenticado.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")

    data = {
        "nickname": current_user.jugador.nickname,
        "user_id": current_user.id,
        "player_id": current_user.jugador.id
    }
    return {"status": "success", "data": data}

# --- Obtener configuración de salas de la nave ---
@router.get("/config", response_model=List[ShipRoomOut], name="Get player ship configuration")
def get_ship_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve una lista con los niveles de todas las salas de la nave del jugador.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")

    # Llamamos al servicio para obtener las salas desde la BD
    salas = ship_rooms_service.obtener_info_salas(db, player_id=current_user.jugador.id)
    
    return salas

# --- Obtener inventario de recursos del jugador ---
@router.get("/resources", response_model=InventoryResponse, name="Get player resources")
def get_player_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve el inventario completo de recursos del jugador autenticado.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")

    # Llamamos al servicio para obtener el inventario desde la BD
    inventario = recursos_service.obtener_inventario_jugador(db, player_id=current_user.jugador.id)
    
    return {"recursos": inventario}

# --- Obtener lista de amigos o aliados ---
@router.get("/friends", name="Get player friends")
def get_friends(current_user: User = Depends(get_current_user)):
    """
    Devuelve la lista de amigos o aliados del jugador.
    """
    data = [
        {"username": "aliado_1", "status": "online"},
        {"username": "aliado_2", "status": "offline"},
    ]
    return {"status": "success", "data": data}


# --- Actualizar configuración del jugador ---
@router.put("/settings", name="Update player settings")
def update_settings(
    settings: dict, current_user: User = Depends(get_current_user)
):
    """
    Actualiza la configuración del jugador (mock).
    """
    # Por ahora solo devolvemos lo que llega
    return {"status": "success", "updated_settings": settings}
