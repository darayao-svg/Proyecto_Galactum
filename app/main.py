# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos Base y engine para crear las tablas
from app.db.session import Base, engine
# Importamos el router principal
from app.api.routes import api_router

# Esta línea asegura que las tablas se creen al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Galactum SGM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Versión final para forzar el despliegue