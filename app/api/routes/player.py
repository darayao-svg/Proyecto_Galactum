from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import get_current_user
from app.models.user import User
import json

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

    try:
        recursos = json.loads(current_user.jugador.inventario)
    except (json.JSONDecodeError, TypeError):
        recursos = {}

    data = {
        "username": current_user.username,
        "resources": recursos,
    }
    return {"status": "success", "data": data}


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
