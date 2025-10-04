from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    class Config:
        from_attributes = True  # permitir convertir desde ORM

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
