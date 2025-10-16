# app/services/auth.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
# ⬇️ Cambiamos a HTTP Bearer (quitamos OAuth2PasswordBearer)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate

settings = get_settings()

# Hash de contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ⬇️ Esquema de autenticación tipo "Bearer <token>"
bearer_scheme = HTTPBearer()  # auto_error=True por defecto: si falta el header, devuelve 401


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, minutes: int | None = None) -> str:
    """
    Genera un JWT con expiración.
    Espera que en `data` venga, por ejemplo, {"sub": "<username|email>"}.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_user_by_ident(db: Session, ident: str) -> User | None:
    """
    Busca por username O email (identificador flexible).
    """
    return (
        db.execute(
            select(User).where((User.username == ident) | (User.email == ident))
        )
        .scalars()
        .first()
    )


def get_current_user(
    db: Session = Depends(get_db),
    # ⬇️ En vez de token: str = Depends(oauth2_scheme)
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    """
    Extrae el token del header Authorization: Bearer <token>,
    lo valida y retorna el usuario autenticado.
    """
    token = credentials.credentials  # el valor del JWT sin la palabra 'Bearer'

    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        sub: str | None = payload.get("sub")
        if sub is None:
            raise cred_exc
    except JWTError:
        # token inválido / expirado / mal firmado
        raise cred_exc

    user = get_user_by_ident(db, sub)
    if not user:
        raise cred_exc
    return user


def register_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = hash_password(user_in.password)
    user = User(username=user_in.username, email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None
