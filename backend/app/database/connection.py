import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

def get_normalized_database_url(url: str) -> str:
    """Normalize DATABASE_URL for SQLAlchemy psycopg3 driver."""
    if not url:
        return ""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = get_normalized_database_url(settings.DATABASE_URL)

engine = None
SessionLocal = None

if DATABASE_URL:
    try:
        # Standard connection pool configuration for Neon serverless PostgreSQL
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.warning(f"Could not initialize database engine: {e}")


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI endpoints providing a database session."""
    if SessionLocal is None:
        raise RuntimeError("Database connection is not configured. Please set DATABASE_URL in .env.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """Test database connectivity and check if pgvector extension is available."""
    if not DATABASE_URL or engine is None:
        return {
            "status": "not_configured",
            "message": "DATABASE_URL is not configured in backend/.env",
            "pgvector_enabled": False,
        }
    try:
        with engine.connect() as conn:
            # Check basic query execution
            res = conn.execute(text("SELECT 1;")).scalar()
            # Check pgvector extension
            vector_res = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
            ).scalar()
            return {
                "status": "connected" if res == 1 else "error",
                "message": "Database connected successfully.",
                "pgvector_enabled": bool(vector_res == "vector"),
            }
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "pgvector_enabled": False,
        }

