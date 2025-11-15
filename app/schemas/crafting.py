# app/schemas/crafting.py
from pydantic import BaseModel

class CraftRequest(BaseModel):
    recipe_id: str
    quantity: int = 1 # Por defecto, craftear 1 unidad

class CraftResponse(BaseModel):
    status: str
    message: str
    crafted_item_id: str
    crafted_quantity: int