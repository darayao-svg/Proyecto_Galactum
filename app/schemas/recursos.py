# app/schemas/recursos.py
from pydantic import BaseModel

class ResourceAdd(BaseModel):
    resource_id: str
    quantity: int

class RecipeConvert(BaseModel):
    recipe_id: str