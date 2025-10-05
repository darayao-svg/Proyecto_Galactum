# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- INICIO DE LA SECCIÓN NUEVA Y CORREGIDA ---
# Importa el motor de la base de datos, la clase Base y TODOS tus modelos
from app.db.session import engine, Base
from app.models.user import User
from app.models.server import Server

# Esta es la línea mágica: le pide a SQLAlchemy que cree todas las tablas
# definidas en tus modelos (User, Server, etc.) en la base de datos
# si es que no existen ya. Se ejecuta cada vez que el servidor se inicia.
print("Verificando y creando tablas de la base de datos si es necesario...")
Base.metadata.create_all(bind=engine)
print("¡Tablas listas!")
# --- FIN DE LA SECCIÓN NUEVA Y CORREGIDA ---

# Importa el "router agregador" que hicimos en app/api/routes/__init__.py
from app.api.routes import api_router

app = FastAPI(
    title="Galactum SGM API",
    version="0.1.0",
)

# CORS abierto por ahora (puedes restringir luego)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta TODOS los routers (health, auth, servers) de una vez
app.include_router(api_router)