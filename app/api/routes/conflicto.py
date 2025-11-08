# app/api/routes/conflicto.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# --- Importaciones Corregidas ---
from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.conflicto import PeticionResolverConflicto, RespuestaResolverConflicto
from app.services import conflicto_service

router = APIRouter(
    prefix="/conflict",
    tags=["Conflicto"]
)

@router.post("/resolve", response_model=RespuestaResolverConflicto)
def ejecutar_conflicto(
    peticion: PeticionResolverConflicto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador atacante no encontrado para este usuario.")

    try:
        # El servicio se encarga de la lógica, el endpoint gestiona la transacción y los errores HTTP.
        resultado = conflicto_service.resolver_conflicto(
            db,
            atacante=current_user.jugador, # Pasamos el objeto Jugador, no el User
            peticion=peticion.model_dump()
        )
        db.commit() # Si la resolución fue exitosa, guardamos los cambios (bajas, botín, etc.)
        return resultado
    except Exception as e:
        db.rollback() # Si algo falla, revertimos todos los cambios en la BD.
        if "Jugador objetivo no encontrado" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "No puedes atacarte a ti mismo" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al resolver el conflicto.")