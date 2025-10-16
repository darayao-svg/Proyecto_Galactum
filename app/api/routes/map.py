from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.ship import get_all_ships
from app.schemas.ship import ShipsResponse
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/map", tags=["map"])

# --- Obtener estado de las naves ---
@router.get("/ships", response_model=ShipsResponse)
def get_ships(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ships = get_all_ships(db)
    return ShipsResponse(status="success", data=ships)


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
