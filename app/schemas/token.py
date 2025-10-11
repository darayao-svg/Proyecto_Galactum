# app/schemas/token.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

# ✅ Este es el nuevo esquema para las respuestas de registro y login
class TokenResponse(BaseModel):
    status: str = "success"
    message: str
    token: str