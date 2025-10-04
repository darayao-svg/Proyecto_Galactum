# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Importa el "router agregador" que hicimos en app/api/routes/__init__.py
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

# ✅ Monta TODOS los routers (health, auth, servers) de una vez
#    Cada router ya define su propio prefix (/api/v1, /api/v1/auth, /api/v1/servers)
app.include_router(api_router)
