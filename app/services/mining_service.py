# app/services/mining_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import uuid

from app.models.asteroid import Asteroid
from app.models.user import User
from app.schemas.mining import MiningInfoResponse, MiningClaimResponse
# Se importa la función del servicio de inventario existente.
# NOTA: 'agregar_equipo' podría no ser el nombre más semántico para recursos,
# pero se usa según lo encontrado en el archivo de referencia.
from app.services.inventory_service import agregar_equipo

def start_mining(db: Session, user: User, asteroid_id: str) -> MiningInfoResponse:
    """
    Inicia el proceso de minado en un asteroide para el usuario actual.
    """
    # 1. Búsqueda y validación del asteroide
    # .with_for_update() es crucial para evitar 'race conditions'
    asteroid = db.query(Asteroid).filter(Asteroid.id == asteroid_id).with_for_update().first()

    if not asteroid or not asteroid.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asteroide no encontrado o inactivo.",
        )

    # --- Validación de Bloqueo ---
    # Si el asteroide está ocupado por OTRO usuario, se lanza un error 409 (Conflict).
    if asteroid.mined_by_id is not None and str(asteroid.mined_by_id) != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asteroide ocupado. Minado termina en: {asteroid.mining_finish_at}",
        )

    # Si el MISMO usuario ya lo está minando, se le devuelve el estado actual sin reiniciar.
    if asteroid.mined_by_id is not None and str(asteroid.mined_by_id) == str(user.id) and asteroid.mining_finish_at:
        now = datetime.utcnow()
        if now < asteroid.mining_finish_at:
            duration_left = asteroid.mining_finish_at - now
            # NOTA: No almacenamos el start_time, por lo que se aproxima para la UI.
            start_time_approx = asteroid.mining_finish_at - timedelta(seconds=5) # Duración base
            return MiningInfoResponse(
                status="already_mining",
                start_time=start_time_approx,
                finish_time=asteroid.mining_finish_at,
                duration_seconds=int(duration_left.total_seconds()),
                expected_yield=10, # Placeholder
            )

    # --- Cálculo ---
    # A modo de ejemplo, la duración es fija. Esto debe cambiarse según lo que pida el front.
    duration_seconds = 5 
    duration = timedelta(seconds=duration_seconds)
    now = datetime.utcnow()
    finish_time = now + duration

    # --- Acción ---
    # Actualiza el asteroide para reflejar que el minado ha comenzado.
    asteroid.mined_by_id = user.id
    asteroid.mining_finish_at = finish_time
    db.commit()
    db.refresh(asteroid)

    # Retorna los datos para MiningInfoResponse.
    return MiningInfoResponse(
        status="mining_started",
        start_time=now,
        finish_time=finish_time,
        duration_seconds=duration_seconds,
        expected_yield=10,  # Placeholder, debería ser dinámico.
    )

def confirma_mining(db: Session, user: User, asteroid_id: str) -> MiningClaimResponse:
    """
    Confirma y reclama los recursos de un minado que ya ha finalizado.
    """
    # Verifica que el asteroide esté bloqueado por ESTE usuario.
    asteroid = db.query(Asteroid).filter(Asteroid.id == asteroid_id).with_for_update().first()

    if not asteroid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asteroide no encontrado.")

    if not asteroid.mined_by_id or str(asteroid.mined_by_id) != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para reclamar los recursos de este asteroide.",
        )

    # Verifica que el tiempo de minado haya transcurrido.
    if datetime.utcnow() < asteroid.mining_finish_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too early. El minado finaliza a las {asteroid.mining_finish_at}",
        )

    # --- Lógica de Recurso ---
    # * cantidad_a_extraer debe ser dinámica (basada en nave, tripulación, etc.).
    cantidad_a_extraer = 10
    
    # * Si ast.cantidad_restante < cantidad_a_extraer, extrae solo lo que queda.
    cantidad_extraida = min(cantidad_a_extraer, asteroid.cantidad_restante)
    resource_type = asteroid.resource_type

    # --- Base de Datos ---
    # * Resta ast.cantidad_restante.
    asteroid.cantidad_restante -= cantidad_extraida
    
    # * Limpia el bloqueo (mined_by_id = None, mining_finish_at = None).
    asteroid.mined_by_id = None
    asteroid.mining_finish_at = None

    if asteroid.cantidad_restante <= 0:
        asteroid.is_active = False
        asteroid.reaparecer_en = datetime.utcnow() + timedelta(minutes=5)

    # * Inventario: Simula la llamada a la función para añadir el recurso.
    if user.jugador:
        agregar_equipo(db=db, player_id=user.jugador.id, item_id=resource_type, quantity=cantidad_extraida)
    else:
        # Esto no debería ocurrir si la data es consistente.
        db.rollback()
        raise HTTPException(status_code=500, detail="Error de consistencia: usuario sin jugador asociado.")

    db.commit()

    # Retorna MiningClaimResponse.
    return MiningClaimResponse(
        resource_obtained=resource_type,
        amount_added=cantidad_extraida,
        asteroid_remaining=asteroid.cantidad_restante,
        inventory_current_weight=None # Opcional: requeriría lógica adicional en inventario.
    )
