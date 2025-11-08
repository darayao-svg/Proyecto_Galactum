# app/api/routes/misiones.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# --- Importaciones Corregidas ---
# Usamos importaciones absolutas para mayor claridad y consistencia con tu proyecto.
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User # Para el tipado de current_user
from app.schemas.misiones import ListaMisionesRespuesta, MisionReclamarPeticion, MisionReclamarRespuesta
from app.services import misiones_service

router = APIRouter(
    prefix="/misiones",
    tags=["Misiones"]
)

@router.get("", response_model=ListaMisionesRespuesta)
def obtener_misiones_jugador(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")
    return misiones_service.obtener_misiones(db, jugador_id=current_user.jugador.id)

@router.post("/reclamar", response_model=MisionReclamarRespuesta)
def reclamar_mision(
    peticion: MisionReclamarPeticion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")
    
    try:
        resultado = misiones_service.reclamar_recompensa(db, jugador_id=current_user.jugador.id, peticion=peticion.model_dump())
        db.commit() # Si todo fue bien en el servicio, confirmamos la transacción.
        return resultado
    except Exception as e:
        db.rollback() # Si algo falló, revertimos todos los cambios.
        if "Misión no completada" in str(e) or "Recompensa ya reclamada" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        if "Misión no encontrada" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        # Para cualquier otro error inesperado
        raise HTTPException(status_code=500, detail="Error interno del servidor")