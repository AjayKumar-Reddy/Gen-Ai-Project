import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.api.chat import router as chat_router
from app.api.colleges import router as colleges_router
from app.api.health import router as health_router
from app.retrieval.bm25_retriever import get_bm25_retriever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("kcet_main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup: warm up in-memory BM25 index
    logger.info("Initializing in-memory BM25 index on startup...")
    try:
        bm25 = get_bm25_retriever()
        logger.info(f"BM25 index ready with {len(bm25.corpus_docs)} documents.")
    except Exception as e:
        logger.warning(f"Could not initialize BM25 index on startup: {e}")
    yield
    logger.info("Shutting down KCET College Assistant application.")


app = FastAPI(
    title="KCET College Assistant API",
    description="AI-powered KCET College Information Assistant using Hybrid RAG (Dense pgvector + BM25 + RRF)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(colleges_router)


@app.get("/")
def read_root():
    return {
        "service": "KCET College Information Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "chat": "/api/chat",
        "colleges": "/api/colleges",
        "cutoffs": "/api/cutoffs",
        "stats": "/api/stats",
    }
