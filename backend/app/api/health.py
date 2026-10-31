from fastapi import APIRouter
from app.config.settings import get_settings
from app.database.connection import check_db_connection

router = APIRouter(prefix="/api", tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_status():
    db_status = check_db_connection()
    return {
        "status": "ok",
        "backend": "online",
        "database": db_status["status"],
        "pgvector": db_status["pgvector_enabled"],
        "dataset_year": settings.DATASET_YEAR,
        "round": settings.COUNSELLING_ROUND,
        "region": settings.SEAT_REGION,
        "embedding_model": settings.GEMINI_EMBEDDING_MODEL,
        "chat_model": settings.GEMINI_CHAT_MODEL,
    }

