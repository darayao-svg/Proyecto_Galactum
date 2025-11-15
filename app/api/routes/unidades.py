# app/api/routes/unidades.py
from fastapi import APIRouter, Depends
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/create", tags=["Unidades"])

@router.post("/unit", summary="Placeholder para crear una unidad")
def create_unit_placeholder(current_user: User = Depends(get_current_user)):
    return {"message": "Endpoint de creación de unidades listo para implementar."}