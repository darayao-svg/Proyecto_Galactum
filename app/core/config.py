from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SECRET_KEY: str = "change_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "postgresql+psycopg2://galactum:galactum@localhost:5432/galactum_db"
    APP_ENV: str = "dev"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "galactum_db"
    db_user: str = "galactum"
    db_password: str = "galactum"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignora variables extra en el .env

@lru_cache
def get_settings():
    return Settings()