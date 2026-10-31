import sys
from app.config.settings import get_settings
from app.database.connection import check_db_connection

def main():
    settings = get_settings()
    print("=" * 60)
    print("KCET Hybrid RAG - Database Configuration & Health Check")
    print("=" * 60)
    print(f"DATABASE_URL Configured: {'YES' if bool(settings.DATABASE_URL) else 'NO (placeholder in .env)'}")
    print(f"Embedding Model: {settings.GEMINI_EMBEDDING_MODEL} (Dim: {settings.EMBEDDING_DIMENSION})")
    print(f"Chat Model: {settings.GEMINI_CHAT_MODEL}")

    result = check_db_connection()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"pgvector Extension Enabled: {result['pgvector_enabled']}")
    print("=" * 60)

    if result["status"] == "connected":
        if result["pgvector_enabled"]:
            print("SUCCESS: Neon PostgreSQL is connected and pgvector extension is active!")
            return 0
        else:
            print("WARNING: Database is connected but pgvector extension is not yet created.")
            print("Run `python -m app.database.schema` to initialize extensions and tables.")
            return 1
    else:
        print("INFO: Please provide your Neon DATABASE_URL in backend/.env to connect.")
        return 0

if __name__ == "__main__":
    sys.exit(main())

