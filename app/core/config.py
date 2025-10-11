# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import validator, AnyUrl
from typing import Dict, Any, Optional
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Galactum API"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        # Corrección para asegurar que no haya doble barra
        path = values.get("DB_NAME", "")
        if not path.startswith("/"):
            path = f"/{path}"

        return str(
            AnyUrl.build(
                scheme="postgresql+psycopg2",
                username=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_HOST"),
                port=int(values.get("DB_PORT")),
                path=path,
            )
        )
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()