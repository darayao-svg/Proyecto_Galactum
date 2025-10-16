# app/api/routes/__init__.py
from fastapi import APIRouter

from app.api.routes.health import router as health
from app.api.routes.auth import router as auth_router
from app.api.routes.server import router as server_router
from app.api.routes.users import router as users
from app.api.routes.db_check import router as dbcheck
from app.api.routes.map import router as map_router
from app.api.routes.player import router as player_routes


api_router = APIRouter()
api_router.include_router(health)
api_router.include_router(auth_router)
api_router.include_router(server_router)
api_router.include_router(users)
api_router.include_router(dbcheck)
api_router.include_router(map_router)
api_router.include_router(player_routes)
