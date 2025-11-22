from pydantic import BaseModel

class CrewAssignRequest(BaseModel):
    slot_id: int

class CrewSpecializeRequest(BaseModel):
    specialization_id: int
