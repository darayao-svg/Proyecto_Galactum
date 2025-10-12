# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
# ✅ Importamos el nuevo esquema de respuesta y los existentes
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.token import TokenResponse
from app.services.auth import (
    get_user_by_ident,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

# El prefijo y las etiquetas que ya tenías son perfectos.
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, name="Register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Tu lógica existente para verificar si el usuario ya existe es perfecta.
    if get_user_by_ident(db, payload.username) or get_user_by_ident(db, payload.email):
        raise HTTPException(status_code=409, detail="Usuario o email ya existe")

    # Tu modelo de usuario es un poco diferente, así que lo adaptamos
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Creamos un token inmediatamente después del registro.
    # Usamos 'username' en el 'sub' del token, como en tu lógica de login.
    token = create_access_token({"sub": user.username})

    # ✅ Devolvemos la respuesta usando el nuevo formato TokenResponse.
    return TokenResponse(message="User registered successfully.", token=token)


@router.post("/login", response_model=TokenResponse, name="Login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Tu lógica de login es perfecta, solo ajustamos la respuesta.
    user = get_user_by_ident(db, payload.username_or_email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token({"sub": user.username})

    # ✅ Devolvemos la respuesta usando el nuevo formato TokenResponse.
    return TokenResponse(message="Login successful.", token=token)


@router.get("/me", response_model=UserOut, name="Me")
def me(current_user: User = Depends(get_current_user)):
    # Este endpoint es muy útil y lo mantenemos como está.
    return current_user