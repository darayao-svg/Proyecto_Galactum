# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.token import TokenResponse
from app.models.user import User
from app.services import auth as auth_service

from app.models.jugador import Player
from app.services.ship_rooms_service import crear_salas_iniciales

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = auth_service.get_user_by_ident(db, payload.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists.")

    # Hashear el password antes de crear el usuario
    hashed_password = auth_service.hash_password(payload.password)
    
    # Crear el nuevo usuario
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.flush() # Para obtener el new_user.id

    # Crear el jugador asociado
    new_player = Player(user_id=new_user.id)
    db.add(new_player)
    db.flush() # Para obtener el new_player.id

    # Crear las salas iniciales para el jugador
    crear_salas_iniciales(db, player_id=new_player.id)

    # Confirmar toda la transacción
    db.commit()
    
    # Refrescar el usuario para asegurar que los datos están actualizados
    db.refresh(new_user)

    # Crear el token de acceso
    token = auth_service.create_access_token({"sub": new_user.username})

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
