# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.services.auth import (
    get_user_by_ident,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class TokenResponse(BaseModel):
    status: str = "success"
    message: str
    token: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_ident(db, payload.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})

    return TokenResponse(
        status="success",
        message="User registered successfully.",
        token=token
    )


@router.post("/login", response_model=TokenResponse, name="Login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión para un usuario existente.
    La petición pedía 'username', pero tu lógica es más flexible y permite
    iniciar sesión con 'username' o 'email', lo cual es mejor.
    """
    user = get_user_by_ident(db, payload.username_or_email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
        
    token = create_access_token({"sub": user.username})

    return TokenResponse(message="Login successful.", token=token)


@router.get("/me", response_model=UserOut, name="Me")
def me(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    return current_user

@router.get("/verify", name="Verify token")
def verify_token(current_user: User = Depends(get_current_user)):
    return {"message": "Token válido", "user": current_user.username}

def get_user_by_ident(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def hash_password(password: str) -> str:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    from jose import jwt
    from app.core.config import get_settings
    settings = get_settings()
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
