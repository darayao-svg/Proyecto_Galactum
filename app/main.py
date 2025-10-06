# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

# --- INICIO DE LA SECCIÓN CRÍTICA (SOLUCIÓN) ---

# 1. Importa la configuración y los componentes de la BD
from app.core.config import get_settings
from app.db.session import Base
from app.models.user import User
from app.models.server import Server
from app.api.routes import api_router

# 2. Carga la configuración desde el entorno de Render
settings = get_settings()

# 3. Imprime la URL para verificar que Render la está leyendo correctamente
print(f"URL DE BASE DE DATOS LEÍDA DEL ENTORNO: {settings.DATABASE_URL}")

# 4. Crea el motor de la base de datos AQUÍ, usando la configuración correcta
engine = create_engine(settings.DATABASE_URL)

# 5. Usa el nuevo motor para crear las tablas
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