from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- INPUTS ---

class CraftRequest(BaseModel):
    # Cambiamos 'recipe_id' por 'item_id' porque el usuario elige QUÉ item quiere crear.
    # Cambiamos str por int.
    item_id: int = Field(..., description="ID del item que se desea craftear")
    quantity: int = Field(1, ge=1, description="Cantidad a craftear (Por defecto 1)")

# --- OUTPUTS ---

class CraftResponse(BaseModel):
    status: str
    message: str
    crafted_item_id: int  # Ahora es int
    crafted_quantity: int
    # Campo opcional para mostrar qué se gastó (lo añadimos en el router)
    consumed_items: Optional[List[Dict[str, Any]]] = None

class RecipeIngredient(BaseModel):
    item_id: int  # Ahora es int
    quantity: int

class RecipeResponse(BaseModel):
    id: int       # ID del item resultante (int)
    name: str
    description: str
    ingredients: List[RecipeIngredient]

# --- LEGACY / OTROS ---
# Actualizamos también estos IDs a int para mantener consistencia 
# con tu tabla CatalogoItem.

class JobResponse(BaseModel):
    status: str
    job_id: str
    completion_time: datetime

class EquipmentItem(BaseModel):
    item_id: int  # int
    name: str
    quantity: int

class EquipmentResponse(BaseModel):
    data: List[EquipmentItem]