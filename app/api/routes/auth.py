# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.models.ship import Ship # 👈 Se añade la importación del nuevo modelo
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.token import TokenResponse 
from app.services.auth import (
    get_user_by_ident,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, name="Register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema y le asigna una nave inicial.
    """
    if get_user_by_ident(db, payload.username) or get_user_by_ident(db, payload.email):
        raise HTTPException(status_code=409, detail="Usuario o email ya existe")

    # Se crea el usuario
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 🎯 Se crea la nave para el nuevo usuario
    new_ship = Ship(owner_id=user.id, current_pos_x=0.0, current_pos_y=0.0)
    db.add(new_ship)
    db.commit()
    
    token = create_access_token({"sub": user.username})
    return TokenResponse(message="User registered successfully.", token=token)


@router.post("/login", response_model=TokenResponse, name="Login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión para un usuario existente.
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