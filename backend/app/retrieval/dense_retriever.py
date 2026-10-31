import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import DocumentRecord
from app.embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class DenseRetriever:
    """
    Performs dense semantic retrieval using Neon PostgreSQL pgvector extension
    with gemini-embedding-001 (768-dim) cosine distance.
    """

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()

    def dense_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute cosine similarity search over pgvector documents in Neon PostgreSQL.
        Returns top_k results with document content, metadata, and similarity score.
        """
        if not query or not query.strip():
            return []

        should_close = False
        if db is None:
            if SessionLocal is None:
                raise RuntimeError("Database connection not configured.")
            db = SessionLocal()
            should_close = True

        try:
            # 1. Generate query embedding vector using Gemini (retrieval_query task)
            query_vector = self.embedding_service.embed_query(query)

            # 2. Build pgvector cosine similarity expression:
            # pgvector cosine_distance <=> is: 1 - cosine_similarity
            # Therefore similarity = 1 - cosine_distance
            cosine_dist = DocumentRecord.embedding.cosine_distance(query_vector)
            similarity = (1 - cosine_dist).label("similarity")

            stmt = select(DocumentRecord, similarity)

            # Apply metadata filters if provided
            filter_clauses = []
            if filters:
                if filters.get("college_code"):
                    filter_clauses.append(
                        DocumentRecord.metadata_["college_code"].as_string()
                        == filters["college_code"].upper()
                    )
                if filters.get("category"):
                    filter_clauses.append(
                        DocumentRecord.metadata_["category"].as_string()
                        == filters["category"].upper()
                    )
                if filters.get("course_code"):
                    filter_clauses.append(
                        DocumentRecord.metadata_["course_code"].as_string()
                        == filters["course_code"].upper()
                    )

            if filter_clauses:
                stmt = stmt.where(and_(*filter_clauses))

            # Filter out records where embedding is null
            stmt = stmt.where(DocumentRecord.embedding.isnot(None))
            stmt = stmt.order_by(cosine_dist.asc()).limit(top_k)

            results = db.execute(stmt).all()

            ranked_docs = []
            for rank_idx, (doc, sim_score) in enumerate(results, start=1):
                ranked_docs.append({
                    "id": doc.id,
                    "cutoff_record_id": doc.cutoff_record_id,
                    "content": doc.content,
                    "metadata": doc.metadata_,
                    "score": float(sim_score) if sim_score is not None else 0.0,
                    "dense_rank": rank_idx,
                    "source": "dense",
                })

            logger.info(f"Dense search retrieved {len(ranked_docs)} documents for query: '{query[:50]}'")
            return ranked_docs
        finally:
            if should_close:
                db.close()


def dense_search(query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    retriever = DenseRetriever()
    return retriever.dense_search(query, top_k=top_k, filters=filters)

