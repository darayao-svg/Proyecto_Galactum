# app/api/routes/__init__.py
from fastapi import APIRouter

from app.api.routes.health import router as health
from app.api.routes.auth import router as auth
from app.api.routes.server import router as servers  # <-- apunta a server.py (singular)

api_router = APIRouter()
api_router.include_router(health)
api_router.include_router(auth)
api_router.include_router(servers)
