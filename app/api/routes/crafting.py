# app/api/routes/crafting.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/craft", tags=["Crafting"])

# Aquí se añadirán los endpoints como POST /item