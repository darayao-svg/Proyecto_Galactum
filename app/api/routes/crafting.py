# app/api/routes/crafting.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services import crafting_service
from app.schemas.crafting import CraftRequest, CraftResponse

router = APIRouter(prefix="/api/v1/craft", tags=["Crafting"])

@router.post("/item", response_model=CraftResponse)
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
        resultado = crafting_service.craft_item(
            db, current_user.jugador.id, peticion.recipe_id, peticion.quantity
        )
        db.commit()
        return CraftResponse(status="success", message=f"Crafteado {resultado['crafted_quantity']}x {resultado['crafted_item_id']}", **resultado)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))