# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import validator, AnyUrl
from typing import Dict, Any, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # --- Configuración de la App (leídas desde el entorno) ---
    PROJECT_NAME: str = "Galactum API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # --- Variables de la Base de Datos ---
    # Estas variables DEBEN ser proporcionadas por el entorno (Render o tu .env)
    # No tienen valores por defecto para forzar la lectura del entorno.
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    # Esta variable se construirá automáticamente
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        # Construye la URL de conexión a partir de las otras variables
        return str(
            AnyUrl.build(
                scheme="postgresql+psycopg2",
                username=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_HOST"),
                port=int(values.get("DB_PORT")),
                path=f"/{values.get('DB_NAME') or ''}",
            )
        )
    
    class Config:
        # Le dice a Pydantic que sea sensible a mayúsculas/minúsculas
        case_sensitive = True
        # Le dice que busque un archivo .env para el desarrollo local
        env_file = ".env"

@lru_cache()
def get_settings():
    # Esta función crea e instancia la configuración una sola vez
    return Settings()