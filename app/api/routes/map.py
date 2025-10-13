from fastapi import APIRouter, Depends
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/map", tags=["map"])

# --- Obtener estado de las naves ---
@router.get("/ships", name="Get ships")
def get_ships(current_user: User = Depends(get_current_user)):
    """
    Devuelve la posición y estado de todas las naves en el sistema solar del jugador.
    (Por ahora se usa información mock hasta conectar con el motor de juego).
    """
    data = [
        {
            "username": current_user.username,
            "isMoving": False,
            "currentPosition": {"x": 150.5, "y": 340.0},
            "startPosition": None,
            "endPosition": None,
        },
        {
            "username": "otro_jugador",
            "isMoving": True,
            "currentPosition": {"x": 820.1, "y": 512.8},
            "startPosition": {"x": 800.0, "y": 500.0},
            "endPosition": {"x": 1200.0, "y": 750.0},
        },
    ]

    return {"status": "success", "data": data}


# --- Obtener información de asteroides ---
@router.get("/asteroids", name="Get asteroids")
def get_asteroids(current_user: User = Depends(get_current_user)):
    """
    Devuelve una lista de asteroides disponibles para minar.
    (Mock data; se integrará luego con el sistema de minería real).
    """
    data = [
        {
            "asteroidId": "AST-001",
            "position": {"x": 250.0, "y": 600.7},
            "resourceType": "Roderitium",
        },
        {
            "asteroidId": "AST-002",
            "position": {"x": -400.2, "y": 120.0},
            "resourceType": "Kliptium",
        },
        {
            "asteroidId": "AST-003",
            "position": {"x": 780.0, "y": -200.5},
            "resourceType": "Aluminium",
        },
    ]
    return {"status": "success", "data": data}
