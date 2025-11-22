# app/schemas/crafting.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class CraftRequest(BaseModel):
    recipe_id: str
    quantity: int = 1 # Por defecto, craftear 1 unidad

class CraftResponse(BaseModel):
    status: str
    message: str
    crafted_item_id: str
    crafted_quantity: int

class RecipeIngredient(BaseModel):
    item_id: str
    quantity: int

class RecipeResponse(BaseModel):
    id: str
    name: str
    description: str
    ingredients: List[RecipeIngredient]

class JobResponse(BaseModel):
    status: str
    job_id: str
    completion_time: datetime

class EquipmentItem(BaseModel):
    item_id: str
    name: str
    quantity: int

class EquipmentResponse(BaseModel):
    data: List[EquipmentItem]