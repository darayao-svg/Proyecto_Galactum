# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- INICIO DE LA SECCIÓN CRÍTICA ---
# Primero, importa todo lo relacionado con la configuración y la base de datos
from app.core.config import get_settings
from app.db.session import engine, Base
from app.models.user import User
from app.models.server import Server
from app.api.routes import api_router

# Obtén la configuración una sola vez
settings = get_settings()

# Imprime la URL para depurar y asegurarte de que es correcta
print(f"CONFIRMACIÓN DE URL DE BASE DE DATOS: {settings.DATABASE_URL}")

# Crea las tablas en la base de datos
print("Verificando y creando tablas de la base de datos si es necesario...")
Base.metadata.create_all(bind=engine)
print("¡Tablas listas!")
# --- FIN DE LA SECCIÓN CRÍTICA ---

# Ahora, crea la aplicación FastAPI
app = FastAPI(
    title="Galactum SGM API",
    version="0.1.0",
)

# Añade el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Finalmente, incluye todos tus routers
app.include_router(api_router)