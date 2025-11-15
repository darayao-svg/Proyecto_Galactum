# app/api/routes/crafting.py
from fastapi import APIRouter, Depends
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/craft", tags=["Crafting"])

@router.post("/item", summary="Placeholder para craftear un item")
def craft_item_placeholder(current_user: User = Depends(get_current_user)):
    return {"message": "Endpoint de crafteo de items listo para implementar."}