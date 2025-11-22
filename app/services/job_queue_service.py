# app/services/job_queue_service.py
from sqlalchemy.orm import Session
from app.models.job import Job

def obtener_jobs(db: Session, player_id: int, tipo: str):
    """
    Obtiene los trabajos pendientes de un jugador para un tipo específico.
    """
    jobs = db.query(Job).filter(
        Job.player_id == player_id,
        Job.job_type == tipo,
        Job.status == 'pending'
    ).all()
    return jobs