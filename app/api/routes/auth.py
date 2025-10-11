# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
# ✅ Importamos el nuevo esquema de respuesta junto a los existentes
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.token import TokenResponse
from app.services.auth import (
    get_user_by_ident,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

# El prefijo y las etiquetas se mantienen igual
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# --- Endpoint de Registro Actualizado ---
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, name="Register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    La petición original solo pedía 'username', pero tu modelo requiere 'email'.
    Mantenemos ambos para que coincida con tu base de datos.
    """
    if get_user_by_ident(db, payload.username):
        raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")
    if get_user_by_ident(db, payload.email):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # ✅ Creamos un token inmediatamente después del registro
    token = create_access_token({"sub": user.username})
    
    # ✅ Devolvemos la respuesta usando el nuevo formato TokenResponse
    return TokenResponse(message="User registered successfully.", token=token)


# --- Endpoint de Login Actualizado ---
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

    # ✅ Devolvemos la respuesta usando el nuevo formato TokenResponse
    return TokenResponse(message="Login successful.", token=token)


# --- Endpoint /me (Sin Cambios) ---
# Este endpoint es muy útil y lo mantenemos como está.
@router.get("/me", response_model=UserOut, name="Me")
def me(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado.
    """
    return current_user