# app/services/recursos_service.py
from sqlalchemy.orm import Session
# ¡Revisa esta importación! Debe apuntar a mi modelo Jugador
from ..models.jugador import Jugador 
import json

def _obtener_inventario(jugador: Jugador) -> dict:
    """Función auxiliar para parsear de forma segura el inventario JSON."""
    if not jugador.inventario:
        return {}
    try:
        return json.loads(jugador.inventario)
    except json.JSONDecodeError:
        return {} # O manejar el error de inventario corrupto

def _guardar_inventario(jugador: Jugador, inventario_dict: dict):
    """Función auxiliar para guardar de forma segura el inventario JSON."""
    jugador.inventario = json.dumps(inventario_dict)


def agregar_recursos_jugador(db: Session, jugador_id: int, lista_recursos: list):
    """
    Añade recursos al inventario de un jugador.
    lista_recursos: [{"id": "Roderitium", "quantity": 100}, {"id": "Kliptium", "quantity": 50}]
    """
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).with_for_update().first()
    if not jugador:
        raise Exception("Jugador no encontrado")
        
    inventario = _obtener_inventario(jugador)
    
    for item in lista_recursos:
        recurso_id = item['id']
        cantidad = item['quantity']
        
        inventario[recurso_id] = inventario.get(recurso_id, 0) + cantidad
        
    _guardar_inventario(jugador, inventario)
    # Nota: No hacemos db.commit() aquí. La función que llama es responsable del commit.

def verificar_y_consumir_recursos(db: Session, jugador_id: int, lista_costos: list):
    """
    Verifica si un jugador tiene suficientes recursos y los consume.
    Si no tiene, lanza una excepción. Es ATÓMICO.
    lista_costos: [{"id": "Roderitium", "qty": 5000}, {"id": "Ore", "qty": 100}]
    """
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).with_for_update().first()
    if not jugador:
        raise Exception("Jugador no encontrado")
        
    inventario = _obtener_inventario(jugador)

    # 1. Fase de Verificación
    for item in lista_costos:
        recurso_id = item['id']
        cantidad_requerida = item['qty']
        
        if inventario.get(recurso_id, 0) < cantidad_requerida:
            raise Exception(f"Recursos insuficientes: Faltan {recurso_id}") # HTTP 400
    # 2. Fase de Consumo
    for item in lista_costos:
        recurso_id = item['id']
        cantidad_requerida = item['qty']
        inventario[recurso_id] -= cantidad_requerida
        
    _guardar_inventario(jugador, inventario)
    # Nota: No hacemos db.commit() aquí. La función que llama es responsable del commit.