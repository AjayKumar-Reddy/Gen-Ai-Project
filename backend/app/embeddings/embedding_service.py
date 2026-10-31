import logging
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config.settings import get_settings
from app.database.connection import SessionLocal
from app.database.models import CutoffRecord, DocumentRecord

logger = logging.getLogger(__name__)
settings = get_settings()


def format_cutoff_document(record: Any) -> str:
    """
    Format a cutoff record into the canonical searchable document representation.
    Preserves all college, course, category, rank, and source metadata together.
    """
    rank_str = str(record.closing_rank) if record.closing_rank is not None else "Not Available"
    return (
        f"College Code: {record.college_code}\n"
        f"College Name: {record.college_name}\n"
        f"Location: {record.location or 'Karnataka'}\n"
        f"Course Code: {record.course_code}\n"
        f"Course Name: {record.course_name}\n"
        f"Category: {record.category}\n"
        f"Closing Rank: {rank_str}\n"
        f"Year: {record.year}\n"
        f"Counselling Round: {record.counselling_round}\n"
        f"Seat Region: {record.seat_region}\n"
        f"Source: Official KCET cutoff PDF\n"
        f"Page: {record.page_number}"
    )


def extract_record_metadata(record: Any) -> Dict[str, Any]:
    """Construct metadata JSON object for vector filtering and source citation."""
    return {
        "cutoff_record_id": record.id,
        "college_code": record.college_code,
        "college_name": record.college_name,
        "location": record.location,
        "course_code": record.course_code,
        "course_name": record.course_name,
        "category": record.category,
        "closing_rank": record.closing_rank,
        "year": record.year,
        "counselling_round": record.counselling_round,
        "seat_region": record.seat_region,
        "source_id": record.source_id,
        "page_number": record.page_number,
    }


class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_API_KEY
        self.model = self.settings.GEMINI_EMBEDDING_MODEL
        self.dimension = self.settings.EMBEDDING_DIMENSION

        # Embeddings for documents
        self.doc_embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model,
            google_api_key=self.api_key,
            output_dimensionality=self.dimension,
            task_type="retrieval_document",
        )

        # Embeddings for user queries
        self.query_embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model,
            google_api_key=self.api_key,
            output_dimensionality=self.dimension,
            task_type="retrieval_query",
        )

    def embed_query(self, query: str) -> List[float]:
        """Generate 768-dimensional embedding for a search query."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")
        return self.query_embeddings.embed_query(query)

    def embed_documents(self, texts: List[str], max_retries: int = 5) -> List[List[float]]:
        """
        Embed a list of document strings with automatic backoff for rate limits.
        """
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")
        
        delay = 2.0
        for attempt in range(max_retries):
            try:
                return self.doc_embeddings.embed_documents(texts)
            except Exception as e:
                err_msg = str(e).lower()
                if "rate" in err_msg or "resource_exhausted" in err_msg or "429" in err_msg:
                    logger.warning(
                        f"Rate limit hit embedding {len(texts)} docs. Retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})..."
                    )
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    logger.error(f"Error embedding documents: {e}")
                    raise e
        raise RuntimeError("Exceeded maximum retries for Gemini embeddings.")

    def sync_cutoff_documents(
        self,
        db: Session = None,
        batch_size: int = 50,
        limit: Optional[int] = None,
        only_non_null: bool = True,
    ) -> Dict[str, Any]:
        """
        Create and populate document representations with pgvector embeddings
        for cutoff records that do not have embeddings yet.
        """
        should_close = False
        if db is None:
            if SessionLocal is None:
                raise RuntimeError("Database connection not configured.")
            db = SessionLocal()
            should_close = True

        try:
            # Query records without corresponding document
            query = (
                db.query(CutoffRecord)
                .outerjoin(DocumentRecord, CutoffRecord.id == DocumentRecord.cutoff_record_id)
                .filter(DocumentRecord.id.is_(None))
            )
            if only_non_null:
                query = query.filter(CutoffRecord.closing_rank.isnot(None))

            if limit:
                query = query.limit(limit)

            records_to_process = query.all()
            total = len(records_to_process)
            logger.info(f"Found {total} cutoff records requiring document embeddings.")

            if total == 0:
                return {"processed": 0, "status": "already_up_to_date"}

            processed_count = 0
            for i in range(0, total, batch_size):
                batch_records = records_to_process[i : i + batch_size]
                texts = [format_cutoff_document(r) for r in batch_records]
                
                # Generate embeddings via Gemini API
                vectors = self.embed_documents(texts)

                # Persist to database
                for r, doc_text, vec in zip(batch_records, texts, vectors):
                    meta = extract_record_metadata(r)
                    doc_entry = DocumentRecord(
                        cutoff_record_id=r.id,
                        content=doc_text,
                        metadata_=meta,
                        embedding=vec,
                    )
                    db.add(doc_entry)

                db.commit()
                processed_count += len(batch_records)
                logger.info(f"Embedded & saved: {processed_count}/{total} documents.")

            return {
                "processed": processed_count,
                "status": "success",
                "embedding_model": self.model,
                "dimension": self.dimension,
            }
        finally:
            if should_close:
                db.close()

