import logging
from sqlalchemy import text
from app.database.connection import engine
from app.database.models import Base

logger = logging.getLogger(__name__)


def init_db():
    """Enable pgvector extension and create all database tables."""
    if engine is None:
        logger.warning("Database engine is not initialized. Skipping init_db.")
        return False

    try:
        with engine.begin() as conn:
            logger.info("Ensuring pgvector extension is created...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

            logger.info("Creating database tables if not exist...")
            Base.metadata.create_all(bind=conn)

            # Create an HNSW index on documents.embedding for fast cosine distance search
            # Using vector_cosine_ops for cosine similarity
            logger.info("Ensuring HNSW cosine index exists on documents(embedding)...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_documents_embedding_hnsw
                ON documents USING hnsw (embedding vector_cosine_ops);
            """))

        logger.info("Database schema initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        raise e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()

