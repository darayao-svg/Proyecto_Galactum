# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base           # <-- Base está en base.py
from app.db.session import engine      # <-- engine está en session.py
from app.api.routes import api_router

# Esta línea asegura que las tablas se creen al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Galactum API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Versión final para forzar el despliegue