# app/schemas/misiones.py
from pydantic import BaseModel
from typing import List, Optional

class Recompensa(BaseModel):
    id: str
    quantity: int

class Mision(BaseModel):
    mision_id: str
    titulo: str
    descripcion: Optional[str]
    progreso_actual: int
    cantidad_requerida: int
    estado: str
    recompensa: List[Recompensa]

    class Config:
        orm_mode = True

class ListaMisionesRespuesta(BaseModel):
    status: str
    misiones_diarias: List[Mision]
    misiones_historia: List[Mision]

class MisionReclamarPeticion(BaseModel):
    mision_id: str

class MisionReclamarRespuesta(BaseModel):
    status: str
    message: str
    recursos_ganados: List[Recompensa]