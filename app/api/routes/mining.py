# app/api/routes/mining.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services import job_queue_service
from app.schemas.crafting import JobResponse

router = APIRouter(prefix="/api/v1/mine", tags=["Mining"])

@router.post("/start/{asteroid_id}", response_model=JobResponse)
def start_mining(
    asteroid_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inicia un trabajo de minería en un asteroide específico.
    """
    try:
        job = job_queue_service.start_mining_job(db, str(current_user.id), asteroid_id)
        db.commit()
        return {"status": "success", "job_id": str(job.id), "completion_time": job.completion_time}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))