import logging
import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import CutoffRecord
from app.embeddings.embedding_service import format_cutoff_document, extract_record_metadata

logger = logging.getLogger(__name__)

# Domain acronym mappings for KCET engineering colleges and branches
ACRONYM_EXPANSIONS = {
    "rvce": ["rv", "r", "v", "rvce", "engineering"],
    "rv": ["rv", "r", "v", "rvce"],
    "msrit": ["msrit", "ramaiah", "m", "s"],
    "ramaiah": ["ramaiah", "msrit"],
    "bmsce": ["bmsce", "bms"],
    "bms": ["bmsce", "bms"],
    "uvce": ["uvce", "visvesvaraya"],
    "dsce": ["dsce", "dayananda", "sagar"],
    "bit": ["bit", "bangalore", "institute"],
    "sit": ["sit", "siddaganga", "tumkur"],
    "nie": ["nie", "national", "institute", "mysore"],
    "pes": ["pes", "pesit", "pesu"],
    "pesit": ["pes", "pesit", "pesu"],
    
    # Common engineering course abbreviations
    "cse": ["computer", "science", "engineering", "cs"],
    "cs": ["computer", "science", "cse"],
    "ece": ["electronics", "communication", "engineering", "ec"],
    "ec": ["electronics", "communication", "ece"],
    "ise": ["information", "science", "engineering", "is"],
    "is": ["information", "science", "ise"],
    "eee": ["electrical", "electronics", "engineering", "ee"],
    "ee": ["electrical", "electronics", "eee"],
    "mech": ["mechanical", "engineering", "me"],
    "me": ["mechanical", "mech"],
    "civil": ["civil", "engineering", "cv"],
    "cv": ["civil", "engineering"],
    "aiml": ["artificial", "intelligence", "machine", "learning", "ai"],
    "ai": ["artificial", "intelligence", "machine", "learning", "aiml"],
    "aids": ["artificial", "intelligence", "data", "science", "ad"],
    "ad": ["artificial", "intelligence", "data", "science", "aids"],
}


def bm25_tokenize(text: str) -> List[str]:
    """
    Tokenize query and documents for BM25 keyword matching.
    Expands common KCET acronyms and handles abbreviations with periods.
    """
    if not text:
        return []

    # Normalize common abbreviations with dots: R. V. -> RV, M. S. -> MS, B. M. S. -> BMS
    clean = re.sub(r"R\.\s*V\.", "RV R V", text, flags=re.IGNORECASE)
    clean = re.sub(r"M\.\s*S\.", "MS M S", clean, flags=re.IGNORECASE)
    clean = re.sub(r"B\.\s*M\.\s*S\.", "BMS B M S", clean, flags=re.IGNORECASE)
    clean = re.sub(r"P\.\s*E\.\s*S\.", "PES P E S", clean, flags=re.IGNORECASE)
    clean = re.sub(r"S\.\s*J\.\s*C\.", "SJC S J C", clean, flags=re.IGNORECASE)

    tokens = re.findall(r"[A-Za-z0-9]+", clean)
    normalized = []
    for t in tokens:
        low = t.lower()
        normalized.append(low)
        # Preserve original uppercase for codes like E005, CS, GM, 2AG
        if t.isupper() and len(t) <= 5:
            normalized.append(t)
        # Check acronyms
        if low in ACRONYM_EXPANSIONS:
            normalized.extend(ACRONYM_EXPANSIONS[low])

    return normalized


class BM25Retriever:
    """
    In-memory BM25 keyword retriever using rank-bm25 (BM25Okapi).
    Maintains document mappings with original document IDs, content, and metadata.
    """

    def __init__(self):
        self.bm25: Optional[BM25Okapi] = None
        self.corpus_docs: List[Dict[str, Any]] = []
        self._is_indexed = False

    def build_index(self, db: Session = None, only_non_null: bool = True):
        """
        Build the in-memory BM25 index from stored cutoff records in Neon PostgreSQL.
        """
        should_close = False
        if db is None:
            if SessionLocal is None:
                raise RuntimeError("Database connection not configured.")
            db = SessionLocal()
            should_close = True

        try:
            logger.info("Building in-memory BM25 index from database records...")
            query = db.query(CutoffRecord)
            if only_non_null:
                query = query.filter(CutoffRecord.closing_rank.isnot(None))

            records = query.all()
            total = len(records)
            logger.info(f"Loaded {total} cutoff records for BM25 indexing.")

            corpus_docs = []
            tokenized_corpus = []

            for r in records:
                content = format_cutoff_document(r)
                meta = extract_record_metadata(r)
                tokens = bm25_tokenize(content)

                corpus_docs.append({
                    "id": r.id,
                    "cutoff_record_id": r.id,
                    "content": content,
                    "metadata": meta,
                })
                tokenized_corpus.append(tokens)

            self.corpus_docs = corpus_docs
            if tokenized_corpus:
                self.bm25 = BM25Okapi(tokenized_corpus)
                self._is_indexed = True
                logger.info(f"BM25 index successfully built with {len(corpus_docs)} documents.")
            else:
                self.bm25 = None
                self._is_indexed = False
                logger.warning("No documents found to build BM25 index.")
        finally:
            if should_close:
                db.close()

    def bm25_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform BM25 search over the document corpus.
        Returns top_k documents with BM25 scores and ranks.
        """
        if not query or not query.strip():
            return []

        if not self._is_indexed or not self.bm25:
            self.build_index()

        query_tokens = bm25_tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        scored_docs = []
        for idx, score in enumerate(scores):
            if score <= 0.0:
                continue

            doc = self.corpus_docs[idx]

            # Optional filter matching
            if filters:
                meta = doc["metadata"]
                if filters.get("college_code") and meta.get("college_code", "").upper() != filters["college_code"].upper():
                    continue
                if filters.get("category") and meta.get("category", "").upper() != filters["category"].upper():
                    continue
                if filters.get("course_code") and meta.get("course_code", "").upper() != filters["course_code"].upper():
                    continue

            scored_docs.append((doc, float(score)))

        # Sort descending by BM25 score
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_results = scored_docs[:top_k]

        ranked_docs = []
        for rank_idx, (doc, score) in enumerate(top_results, start=1):
            ranked_docs.append({
                "id": doc["id"],
                "cutoff_record_id": doc["cutoff_record_id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": score,
                "bm25_rank": rank_idx,
                "source": "bm25",
            })

        logger.info(f"BM25 search retrieved {len(ranked_docs)} documents for query: '{query[:50]}'")
        return ranked_docs


_bm25_retriever: Optional[BM25Retriever] = None


def get_bm25_retriever() -> BM25Retriever:
    global _bm25_retriever
    if _bm25_retriever is None:
        _bm25_retriever = BM25Retriever()
        _bm25_retriever.build_index()
    return _bm25_retriever


def bm25_search(query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    retriever = get_bm25_retriever()
    return retriever.bm25_search(query, top_k=top_k, filters=filters)
