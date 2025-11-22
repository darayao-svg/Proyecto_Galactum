from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tripulante import Tripulante
from app.models.ship_rooms import ShipRoom
from app.models.inventory import Inventory
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obtener_tripulantes(db: Session, player_id: int):
    """
    Obtiene todos los tripulantes de un jugador.
    """
    return db.query(Tripulante).filter(Tripulante.player_id == player_id).all()

def asignar_tripulante(db: Session, player_id: int, crew_id: int, slot_id: int):
    """
    Asigna un tripulante a una sala de la nave.
    """
    # Verificar que el tripulante pertenece al jugador
    tripulante = db.query(Tripulante).filter(Tripulante.id == crew_id, Tripulante.player_id == player_id).first()
    if not tripulante:
        raise HTTPException(status_code=404, detail="Tripulante no encontrado.")

    # Verificar que la sala pertenece al jugador
    sala = db.query(ShipRoom).filter(ShipRoom.id == slot_id, ShipRoom.player_id == player_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada.")

    # Verificar si la sala ya está ocupada
    if sala.tripulante:
        raise HTTPException(status_code=400, detail="La sala ya está ocupada.")

    # Desasignar el tripulante de cualquier otra sala
    if tripulante.slot_id is not None:
        sala_anterior = db.query(ShipRoom).filter(ShipRoom.id == tripulante.slot_id).first()
        if sala_anterior:
            # Esto es una inconsistencia de datos si ocurre, pero lo manejamos por si acaso
            logger.warning(f"Inconsistencia: El tripulante {crew_id} estaba en la sala {tripulante.slot_id} que ya no tiene referencia a él.")

    # Asignar a la nueva sala
    tripulante.slot_id = slot_id # type: ignore
    db.commit()
    db.refresh(tripulante)
    
    return {"status": "success", "message": f"Tripulante {tripulante.nombre} asignado a la sala {sala.room_id}."}

def subir_nivel_tripulante(db: Session, player_id: int, crew_id: int):
    """
    Sube de nivel a un tripulante, con un coste de recursos.
    """
    tripulante = db.query(Tripulante).filter(Tripulante.id == crew_id, Tripulante.player_id == player_id).first()
    if not tripulante:
        raise HTTPException(status_code=404, detail="Tripulante no encontrado.")

    # Lógica de coste (ejemplo: 100 de 'Roderitium' por nivel)
    coste_recurso = "Roderitium"
    coste_cantidad = 100 * tripulante.nivel

    inventario_jugador = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.resource_id == coste_recurso
    ).first()

    if not inventario_jugador or inventario_jugador.quantity < coste_cantidad: # type: ignore
        raise HTTPException(status_code=400, detail=f"Recursos insuficientes. Se necesitan {coste_cantidad} de {coste_recurso}.")

    # Actualizar nivel y recursos
    inventario_jugador.quantity -= coste_cantidad # type: ignore
    tripulante.nivel += 1 # type: ignore
    db.commit()
    db.refresh(tripulante)
    db.refresh(inventario_jugador)

    return {"status": "success", "message": f"Tripulante {tripulante.nombre} ha subido al nivel {tripulante.nivel}."}

def especializar_tripulante(db: Session, player_id: int, crew_id: int, specialization_id: int):
    """
    Asigna una especialización a un tripulante.
    """
    # Este es un ejemplo. Deberías tener una tabla de especializaciones.
    especializaciones_validas = {
        1: "Ingeniero",
        2: "Científico",
        3: "Táctico"
    }

    if specialization_id not in especializaciones_validas:
        raise HTTPException(status_code=400, detail="Especialización no válida.")

    tripulante = db.query(Tripulante).filter(Tripulante.id == crew_id, Tripulante.player_id == player_id).first()
    if not tripulante:
        raise HTTPException(status_code=404, detail="Tripulante no encontrado.")

    # Lógica de coste (ejemplo: 500 de 'Kliptium')
    coste_recurso = "Kliptium"
    coste_cantidad = 500

    inventario_jugador = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.resource_id == coste_recurso
    ).first()

    if not inventario_jugador or inventario_jugador.quantity < coste_cantidad: # type: ignore
        raise HTTPException(status_code=400, detail=f"Recursos insuficientes. Se necesitan {coste_cantidad} de {coste_recurso}.")

    # Actualizar especialización y recursos
    inventario_jugador.quantity -= coste_cantidad # type: ignore
    tripulante.especializacion = especializaciones_validas[specialization_id] # type: ignore
    db.commit()
    db.refresh(tripulante)
    db.refresh(inventario_jugador)

    return {"status": "success", "message": f"Tripulante {tripulante.nombre} ahora es {tripulante.especializacion}."}