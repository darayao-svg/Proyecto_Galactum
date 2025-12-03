from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any, Dict

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.models.crafting import RecetaCrafteo, catalogo_items 

# --- SERVICIOS ---
from app.services import crafting_service, inventory_service 
# job_queue_service comentado hasta refactorizarlo
# from app.services import job_queue_service 

# --- SCHEMAS ---
from app.schemas.crafting import (
    CraftRequest, 
    CraftResponse, 
    RecipeResponse, 
    RecipeIngredient,
    EquipmentResponse,
    # JobResponse  <-- Comentado temporalmente
)

router = APIRouter(tags=["Crafting"])

# -----------------------------------------------------------------------------
# 1. ENDPOINT DE CRAFTEO INMEDIATO (SIN TIEMPO)
# -----------------------------------------------------------------------------
@router.post("/api/v1/craft/item", response_model=CraftResponse, summary="Craftear un item")
def craft_item_endpoint(
    peticion: CraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Craftea un ítem inmediatamente buscando su receta en la base de datos relacional
    y consumiendo los recursos del inventario del jugador.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    try:
        # Llamamos al servicio actualizado
        resultado = crafting_service.craftear_recurso(
            db=db, 
            jugador_id=current_user.jugador.id, 
            item_resultado_id=peticion.item_id
        )
        
        # Commit de la transacción
        db.commit()

        # Mapeo de respuesta
        return CraftResponse(
            status="success", 
            message=resultado["mensaje"],
            crafted_item_id=resultado["item_id"],
            crafted_quantity=resultado["producidos"][0]["quantity"],
            consumed_items=resultado["consumidos"] # Asegúrate de haber agregado esto a tu Schema CraftResponse
        )

    except ValueError as e:
        db.rollback()
        # Error 400: Bad Request (Faltan materiales o receta no existe)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        db.rollback()
        print(f"Error crítico en crafting: {e}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor.")

# -----------------------------------------------------------------------------
# 2. ENDPOINTS DE INFORMACIÓN (RECETAS DISPONIBLES)
# -----------------------------------------------------------------------------

def _obtener_recetas_por_tipo(db: Session, tipos_item: List[str]) -> List[RecipeResponse]:
    """
    Función auxiliar para buscar items de ciertos tipos y formatearlos como recetas.
    """
    # 1. Buscar items en el catálogo que coincidan con los tipos solicitados
    items_catalogo = db.query(catalogo_items).filter(catalogo_items.tipo.in_(tipos_item)).all()
    
    lista_respuesta = []

    for item in items_catalogo:
        # 2. Buscar si este item tiene una receta definida
        ingredientes_db = db.query(RecetaCrafteo).filter(
            RecetaCrafteo.item_resultado_id == item.id
        ).all()

        # Si tiene ingredientes, lo agregamos a la lista de "Recetas Visibles"
        if ingredientes_db:
            ingredientes_format = [
                RecipeIngredient(
                    item_id=ing.item_requerido_id, # Asumiendo que tu schema ahora usa int
                    quantity=ing.cantidad
                ) for ing in ingredientes_db
            ]

            lista_respuesta.append(RecipeResponse(
                id=item.id,          # ID del item resultante
                name=item.nombre,
                description=item.descripcion or "",
                ingredients=ingredientes_format
            ))
            
    return lista_respuesta

@router.get("/api/v1/factory/recipes", response_model=List[RecipeResponse])
def get_factory_recipes(db: Session = Depends(get_db)):
    """
    Obtiene recetas para la Fábrica (Recursos, Componentes, Materiales).
    """
    # Define aquí qué 'tipos' de items se hacen en la fábrica
    tipos_fabrica = ['recurso', 'componente', 'material']
    return _obtener_recetas_por_tipo(db, tipos_fabrica)

@router.get("/api/v1/armory/blueprints", response_model=List[RecipeResponse])
def get_armory_blueprints(db: Session = Depends(get_db)):
    """
    Obtiene recetas (planos) para la Armería (Armas, Munición, Equipamiento).
    """
    # Define aquí qué 'tipos' de items se hacen en la armería
    tipos_armeria = ['arma', 'municion', 'equipamiento']
    return _obtener_recetas_por_tipo(db, tipos_armeria)

# -----------------------------------------------------------------------------
# 3. ENDPOINTS DE EQUIPAMIENTO
# -----------------------------------------------------------------------------
@router.get("/api/v1/player/equipment", response_model=EquipmentResponse)
def get_player_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el equipamiento actual del jugador.
    """
    if not current_user.jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    # Asegúrate que inventory_service.obtener_equipo maneje los IDs nuevos correctamente
    equipment = inventory_service.obtener_equipo(db, current_user.jugador.id)
    return {"data": equipment}

# -----------------------------------------------------------------------------
# 4. SECCIÓN LEGACY / COLA DE TRABAJO (COMENTADO TEMPORALMENTE)
# -----------------------------------------------------------------------------
# Estos endpoints requieren refactorizar job_queue_service para usar IDs enteros
# y la nueva estructura de DB. Se comentan para evitar errores de ejecución.

# @router.post("/api/v1/craft/{recipe_or_blueprint_id}", response_model=JobResponse)
# def start_crafting_job(
#     recipe_or_blueprint_id: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     [PENDIENTE DE REFACTOR] Inicia un trabajo de crafteo asíncrono.
#     """
#     pass 

# @router.get("/api/v1/crafting/queue", response_model=List[Dict[str, Any]])
# def get_crafting_queue(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     [PENDIENTE DE REFACTOR] Obtiene la cola de trabajos.
#     """
#     pass