# app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["default"])

@router.get("/health", name="Health")
def health():
    return {"status": "ok"}
