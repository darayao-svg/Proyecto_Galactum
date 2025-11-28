# app/services/crafting_service.py
# app/services/crafting_service.py
from sqlalchemy.orm import Session
from app.models.crafting import Recipe  # CORRECCIÓN: Usar el modelo Recipe existente
from app.models.ship_rooms import ShipRoom # CORRECCIÓN: Usar el modelo ShipRoom existente
from app.services.recursos_service import verificar_y_consumir_recursos, agregar_recursos_jugador # CORRECCIÓN: Importar la función correcta
import json
from typing import cast

def craftear_recurso(db: Session, jugador_id: int, receta_id: str): # El ID de la receta es un string
    """
    Gestiona la lógica de crafteo para un jugador.

    1. Valida la receta y los prerrequisitos del jugador.
    2. Ejecuta una transacción atómica para consumir recursos de entrada y añadir los de salida.
    """
    # 1. OBTENER LA RECETA
    receta_db = db.query(Recipe).filter(Recipe.id == receta_id).first()
    if not receta_db:
        raise ValueError("La receta especificada no existe.")

    # 2. VERIFICAR PRERREQUISITOS (NIVEL DE SALA)
    # Asumimos que el 'type' de la receta ('fabrica' o 'armeria') corresponde al 'room_id' de la sala.
    # Y que el nivel requerido es 1 por defecto (puedes añadir una columna a tu modelo Recipe si necesitas más flexibilidad).
    # Usamos `cast` para decirle a Pylance que trate esto como un string, no como una columna.
    sala_requerida_id = cast(str, receta_db.type)
    nivel_sala_requerido = 1  # Asumimos nivel 1, ya que no está en el modelo Recipe

    # Si la receta especifica un tipo de sala, verificamos los prerrequisitos.
    # Usamos un `if` simple para que Pylance no se confunda.
    if sala_requerida_id:
        sala_jugador = db.query(ShipRoom).filter(
            ShipRoom.player_id == jugador_id,
            ShipRoom.room_id == sala_requerida_id
        ).first()

        # Separamos las comprobaciones para mayor claridad y para ayudar al linter.
        if sala_jugador is None:
            raise PermissionError(
                f"Se requiere la sala '{sala_requerida_id}' para craftear este item."
            )
        # Usamos `cast` de nuevo para la comparación numérica.
        if cast(int, sala_jugador.level) < nivel_sala_requerido:
            raise PermissionError(
                f"Se requiere la sala '{sala_requerida_id}' a nivel {nivel_sala_requerido}."
            )

    # Parsear datos JSON de la receta
    try:
        # CORRECCIÓN: Asignamos a una variable para asegurar que el tipo es una lista.
        ingredients_data = receta_db.ingredients
        recursos_entrada: list = ingredients_data if isinstance(ingredients_data, list) else []
        # Asumimos que la salida es 1 unidad del item que representa la receta.
        recursos_salida = [{"id": receta_db.id, "quantity": 1}]
    except (json.JSONDecodeError, TypeError):
        raise ValueError("Formato de datos de receta inválido.")

    # --- INICIO DE LA TRANSACCIÓN LÓGICA ---
    # La atomicidad la garantiza el patrón de Session de FastAPI.
    # Si alguna de las siguientes operaciones falla, se hará rollback.

    # 3. VERIFICAR Y CONSUMIR RECURSOS DE ENTRADA
    try:
        verificar_y_consumir_recursos(db, jugador_id, recursos_entrada) # Ahora el tipo es correcto.
    except ValueError as e:
        # Re-lanzamos la excepción con un mensaje más específico para el crafteo.
        raise ValueError(f"Recursos insuficientes para craftear: {e}") from e

    # 4. AÑADIR RECURSOS/ITEMS DE SALIDA
    agregar_recursos_jugador(db, jugador_id, recursos_salida) # CORRECCIÓN: Usar la función correcta

    # --- FIN DE LA TRANSACCIÓN LÓGICA ---
    # El commit se gestionará en el endpoint.

    # 5. RESPUESTA
    # El servicio devuelve los datos para que el endpoint construya la respuesta HTTP.
    return {
        "consumed": recursos_entrada,
        "produced": recursos_salida
    }