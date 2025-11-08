# app/api/routes/tripulantes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# --- Importaciones Corregidas ---
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.tripulantes import (
    TripulanteContratarPeticion, TripulanteMejorarPeticion, TripulanteAccionRespuesta
)
from app.services import tripulantes_service

router = APIRouter(
    prefix="/tripulantes",
    tags=["Tripulantes"]
)

@router.post("/contratar", response_model=TripulanteAccionRespuesta)
def contratar_nuevo_tripulante(
    peticion: TripulanteContratarPeticion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")

    try:
        resultado = tripulantes_service.contratar_tripulante(db, jugador_id=current_user.jugador.id, peticion=peticion.model_dump())
        db.commit()
        return resultado
    except Exception as e:
        db.rollback()
        if "Costo de tripulante no definido" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "Recursos insuficientes" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al contratar tripulante.")

@router.post("/mejorar", response_model=TripulanteAccionRespuesta)
def mejorar_tripulante_existente(
    peticion: TripulanteMejorarPeticion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")

    try:
        resultado = tripulantes_service.mejorar_tripulante(db, jugador_id=current_user.jugador.id, peticion=peticion.model_dump())
        db.commit()
        return resultado
    except Exception as e:
        db.rollback()
        if "no encontrado" in str(e) or "no definido" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "Recursos insuficientes" in str(e) or "nivel objetivo debe ser superior" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al mejorar tripulante.")