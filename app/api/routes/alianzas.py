# app/api/routes/alianzas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# --- Importaciones Corregidas ---
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.alianzas import (
    AlianzaCrearPeticion, AlianzaRespuesta, AsedioIniciarRespuesta
)
from app.services import alianzas_service

router = APIRouter(
    prefix="/alianzas",
    tags=["Alianzas"]
)

@router.post("", response_model=AlianzaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_nueva_alianza(
    peticion: AlianzaCrearPeticion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")
    
    try:
        nueva_alianza = alianzas_service.crear_alianza(db, jugador_id=current_user.jugador.id, peticion=peticion.model_dump())
        db.commit()
        db.refresh(nueva_alianza)
        return nueva_alianza
    except Exception as e:
        db.rollback()
        if "ya existe" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        if "ya pertenece a una alianza" in str(e) or "Recursos insuficientes" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al crear la alianza.")

@router.post("/asedio/{planeta_id}", response_model=AsedioIniciarRespuesta)
def iniciar_asedio_planeta(
    planeta_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado para este usuario.")
        
    try:
        nuevo_asedio = alianzas_service.iniciar_asedio(db, jugador_id=current_user.jugador.id, planeta_id=planeta_id)
        db.commit()
        db.refresh(nuevo_asedio)
        return AsedioIniciarRespuesta(
            status="siege_started",
            message=f"El asedio en '{planeta_id}' ha comenzado.",
            asedio_id=nuevo_asedio.asedio_id,
            fecha_fin=nuevo_asedio.fecha_fin
        )
    except Exception as e:
        db.rollback()
        if "No autorizado" in str(e):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        if "ya está bajo asedio" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# NOTA: El endpoint para reforzar asedios se omite por ahora, ya que la lógica
# para consumir unidades aún no está implementada en el servicio.
# Una vez que se añada, se puede crear el endpoint correspondiente.