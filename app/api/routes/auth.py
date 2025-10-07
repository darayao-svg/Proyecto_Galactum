# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.services.auth import (
    get_user_by_ident,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

# ✅ prefijo correcto
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, name="Register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # ¿ya existe username o email?
    if get_user_by_ident(db, payload.username) or get_user_by_ident(db, payload.email):
        raise HTTPException(status_code=409, detail="Usuario o email ya existe")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token, name="Login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_ident(db, payload.username_or_email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut, name="Me")
def me(current_user: User = Depends(get_current_user)):
    return current_user
