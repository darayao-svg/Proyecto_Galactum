# app/schemas/token.py
from pydantic import BaseModel

# Este es el nuevo esquema para las respuestas de registro y login
class TokenResponse(BaseModel):
    status: str = "success"
    message: str
    token: str