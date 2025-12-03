# app/api/routes/mining.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services import mining_service
from app.schemas.mining import MiningStartRequest, MiningInfoResponse, MiningClaimResponse

# Se agrupan las rutas bajo el prefijo /mining
router = APIRouter(prefix="/api/v1/mining", tags=["Mining"])

@router.post("/start", response_model=MiningInfoResponse, status_code=status.HTTP_200_OK)
def start_mining_endpoint(
    request: MiningStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    1. POST /start: Usa MiningStartRequest y devuelve MiningInfoResponse.

    Inicia el proceso de minado en un asteroide, bloqueándolo para el usuario.
    Devuelve la información sobre el tiempo de finalización.
    """
    mining_info = mining_service.start_mining(
        db=db,
        user=current_user,
        asteroid_id=request.asteroid_id
    )
    return mining_info

@router.post("/claim", response_model=MiningClaimResponse, status_code=status.HTTP_200_OK)
def claim_mining_rewards_endpoint(
    request: MiningStartRequest, # Se reutiliza el request para obtener el asteroid_id
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    2. POST /claim: Usa un body simple con asteroid_id y devuelve MiningClaimResponse.

    Reclama los recursos una vez que el tiempo de minado ha concluido.
    Verifica que el tiempo se haya cumplido y que el reclamante sea el minero original.
    """
    claim_response = mining_service.confirma_mining(
        db=db,
        user=current_user,
        asteroid_id=request.asteroid_id
    )
    return claim_response