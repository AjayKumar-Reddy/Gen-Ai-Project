import logging
import time

import numpy as np
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, insert
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


# Instruction prefix recommended by BAAI for bge-*-en-v1.5 retrieval queries
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

_LOCAL_MODELS: Dict[str, Any] = {}


def _get_local_model(name: str):
    """Load a sentence-transformers model once per process (Apple MPS GPU if available)."""
    if name not in _LOCAL_MODELS:
        import torch
        from sentence_transformers import SentenceTransformer

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"Loading local embedding model '{name}' on {device}...")
        try:
            # Use the cached copy without contacting the Hugging Face hub
            # (hub checks can stall and block start-up).
            _LOCAL_MODELS[name] = SentenceTransformer(name, device=device, local_files_only=True)
        except Exception:
            logger.info("Model not cached yet; downloading from Hugging Face...")
            _LOCAL_MODELS[name] = SentenceTransformer(name, device=device)
        logger.info("Local embedding model loaded.")
    return _LOCAL_MODELS[name]


class EmbeddingService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_API_KEY
        self.provider = self.settings.EMBEDDING_PROVIDER.lower()
        self.dimension = self.settings.EMBEDDING_DIMENSION

        if self.provider == "local":
            self.model = self.settings.LOCAL_EMBEDDING_MODEL
            self.doc_embeddings = None
            self.query_embeddings = None
            return

        self.model = self.settings.GEMINI_EMBEDDING_MODEL

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
        if self.provider == "local":
            vec = _get_local_model(self.model).encode(
                BGE_QUERY_INSTRUCTION + query, normalize_embeddings=True
            )
            return [float(x) for x in vec]
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")
        return self.query_embeddings.embed_query(query)

    def embed_documents(self, texts: List[str], max_retries: int = 10) -> List[List[float]]:
        """
        Embed a list of document strings with automatic backoff for rate limits.
        Gemini free-tier limits are per minute, so back-off grows to ~2 minutes
        (total patience ~12 minutes) before giving up.
        """
        if self.provider == "local":
            vecs = _get_local_model(self.model).encode(
                texts, batch_size=64, normalize_embeddings=True
            )
            return [[float(x) for x in v] for v in vecs]
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")

        delay = 5.0
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
                    delay = min(delay * 2.0, 120.0)
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
        categories: Optional[List[str]] = None,
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
            # 0. Remove stale documents whose text no longer matches their cutoff
            # record (e.g. after a re-ingestion corrected a rank or course name),
            # or whose record no longer has a closing rank. They are re-embedded below.
            stale_doc_ids = []
            # Select only id + content (not the embedding vectors) to keep this cheap.
            # A document is also stale if it was embedded by a different model
            # (vectors from different models are not comparable).
            for doc_id, doc_content, doc_meta, rec in db.query(
                DocumentRecord.id, DocumentRecord.content, DocumentRecord.metadata_, CutoffRecord
            ).join(CutoffRecord, CutoffRecord.id == DocumentRecord.cutoff_record_id):
                if (
                    doc_content != format_cutoff_document(rec)
                    or (only_non_null and rec.closing_rank is None)
                    or (doc_meta or {}).get("embedding_model") != self.model
                ):
                    stale_doc_ids.append(doc_id)
            for i in range(0, len(stale_doc_ids), 1000):
                db.query(DocumentRecord).filter(
                    DocumentRecord.id.in_(stale_doc_ids[i : i + 1000])
                ).delete(synchronize_session=False)
            db.commit()
            if stale_doc_ids:
                logger.info(f"Removed {len(stale_doc_ids)} stale documents for re-embedding.")

            # Query records without corresponding document
            query = (
                db.query(CutoffRecord)
                .outerjoin(DocumentRecord, CutoffRecord.id == DocumentRecord.cutoff_record_id)
                .filter(DocumentRecord.id.is_(None))
            )
            if only_non_null:
                query = query.filter(CutoffRecord.closing_rank.isnot(None))
            if categories:
                query = query.filter(CutoffRecord.category.in_([c.upper() for c in categories]))

            if limit:
                query = query.limit(limit)

            records_to_process = query.all()
            total = len(records_to_process)
            logger.info(f"Found {total} cutoff records requiring document embeddings.")

            if total == 0:
                return {"processed": 0, "status": "already_up_to_date"}

            # For large loads, maintaining the HNSW graph on every insert is very
            # slow; drop the index, bulk insert, then rebuild it once at the end.
            rebuild_index = total > 2000
            if rebuild_index:
                logger.info("Dropping HNSW index for bulk load (rebuilt at the end)...")
                db.execute(text("DROP INDEX IF EXISTS ix_documents_embedding_hnsw"))
                db.commit()

            processed_count = 0
            try:
                self._embed_and_insert(db, records_to_process, batch_size, total)
                processed_count = total
            finally:
                # Always make sure the index exists (an interrupted earlier bulk
                # load may have left it dropped). No-op if it already exists.
                logger.info("Ensuring HNSW cosine index on documents(embedding)...")
                db.rollback()
                db.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_documents_embedding_hnsw "
                    "ON documents USING hnsw (embedding vector_cosine_ops)"
                ))
                db.commit()
                logger.info("HNSW index ready.")

            return {
                "processed": processed_count,
                "status": "success",
                "embedding_model": self.model,
                "dimension": self.dimension,
            }
        finally:
            if should_close:
                db.close()

    def _embed_and_insert(self, db: Session, records_to_process: List[Any], batch_size: int, total: int):
        """Embed records in batches and bulk-insert them into the documents table."""
        processed_count = 0
        for i in range(0, total, batch_size):
            batch_records = records_to_process[i : i + batch_size]
            texts = [format_cutoff_document(r) for r in batch_records]
            
            # Generate embeddings (local model or Gemini API)
            vectors = self.embed_documents(texts)

            # Persist with a binary COPY: vectors are sent as 4-byte floats
            # (~3 KB/row) instead of text (~15 KB/row), which is several times
            # faster over the network than an INSERT.
            raw_conn = db.connection().connection.driver_connection
            register_vector(raw_conn)
            with raw_conn.cursor().copy(
                "COPY documents (cutoff_record_id, content, metadata, embedding) "
                "FROM STDIN WITH (FORMAT BINARY)"
            ) as copy:
                copy.set_types(["int4", "text", "jsonb", "vector"])
                for r, doc_text, vec in zip(batch_records, texts, vectors):
                    meta = extract_record_metadata(r)
                    meta["embedding_model"] = self.model
                    copy.write_row(
                        # Jsonb(...) sends the dict as a JSON object; passing a
                        # pre-encoded string would store a JSON *string* instead.
                        (r.id, doc_text, Jsonb(meta), np.asarray(vec, dtype=np.float32))
                    )
            db.commit()
            processed_count += len(batch_records)
            logger.info(f"Embedded & saved: {processed_count}/{total} documents.")

