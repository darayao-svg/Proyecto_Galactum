# app/schemas/mining.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MiningStartRequest(BaseModel):
    asteroid_id: str

class MiningInfoResponse(BaseModel):
    status: str
    start_time: datetime
    finish_time: datetime
    duration_seconds: int
    expected_yield: int

class MiningClaimResponse(BaseModel):
    resource_obtained: str
    amount_added: int
    asteroid_remaining: int
    inventory_current_weight: Optional[int] = None
