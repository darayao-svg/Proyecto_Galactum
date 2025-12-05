# app/schemas/mining.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MiningStartRequest(BaseModel):
    asteroid_id: str

class MiningInfoResponse(BaseModel):
    status: str = Field(..., alias="estado")
    start_time: datetime = Field(..., alias="tiempo_inicio")
    finish_time: datetime = Field(..., alias="tiempo_fin")
    duration_seconds: int = Field(..., alias="duracion_segundos")
    expected_yield: int = Field(..., alias="rendimiento_esperado")
    resource_id: int = Field(..., alias="recurso_id")
    mining_speed: float = Field(..., alias="velocidad_minado")
    resource_name: str = Field(..., alias="nombre_recurso")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class MiningClaimResponse(BaseModel):
    resource_name: str = Field(..., alias="nombre_recurso")
    amount_added: int = Field(..., alias="cantidad_agregada")
    asteroid_remaining: int = Field(..., alias="cantidad_restante_asteroide")
    # inventory_current_weight: Optional[int] = Field(None, alias="peso_actual_inventario")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
