# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.token import TokenResponse
from app.models.user import User
from app.services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = auth_service.get_user_by_ident(db, payload.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=auth_service.hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth_service.create_access_token({"sub": user.username})

    return TokenResponse(
        status="success",
        message="User registered successfully.",
        token=token
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.get_user_by_ident(db, payload.username)
    if not user or not auth_service.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = auth_service.create_access_token({"sub": user.username})

    return TokenResponse(
        status="success",
        message="Login successful.",
        token=token
    )


@router.get("/me", response_model=UserOut, name="Me")
def me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    return current_user

@router.get("/verify", name="Verify token")
def verify_token(current_user: User = Depends(auth_service.get_current_user)):
    return {"message": "Token válido", "user": current_user.username}
