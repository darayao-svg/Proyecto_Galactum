# app/api/routes/unidades.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/create", tags=["Unidades"])

# Aquí se añadirán los endpoints como POST /unit