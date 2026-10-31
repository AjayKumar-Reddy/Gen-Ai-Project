import logging
from typing import List, Dict, Any, Optional

from app.config.settings import get_settings
from app.retrieval.dense_retriever import DenseRetriever, dense_search
from app.retrieval.bm25_retriever import BM25Retriever, get_bm25_retriever
from app.retrieval.rrf import reciprocal_rank_fusion

logger = logging.getLogger(__name__)
settings = get_settings()


class HybridRetriever:
    """
    Hybrid Retriever combining Dense Vector Search (pgvector)
    and Sparse Keyword Search (BM25) using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        dense_retriever: Optional[DenseRetriever] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        rrf_k: int = 60,
    ):
        self.dense_retriever = dense_retriever or DenseRetriever()
        self.bm25_retriever = bm25_retriever or get_bm25_retriever()
        self.rrf_k = rrf_k or settings.RRF_K

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        dense_top_k: int = 10,
        bm25_top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Execute independent Dense and BM25 searches and fuse rankings using RRF.

        Returns:
            {
                "query": query,
                "fused_results": [...],
                "dense_results": [...],
                "bm25_results": [...],
                "metadata": {
                    "dense_count": int,
                    "bm25_count": int,
                    "fused_count": int,
                    "rrf_k": int
                }
            }
        """
        logger.info(f"Initiating Hybrid Search for query: '{query}'")

        # 1. Execute Dense Retrieval
        dense_results: List[Dict[str, Any]] = []
        try:
            dense_results = self.dense_retriever.dense_search(
                query=query,
                top_k=dense_top_k,
                filters=filters,
            )
        except Exception as e:
            logger.warning(f"Dense retrieval error (falling back to BM25): {e}")

        # 2. Execute BM25 Keyword Retrieval
        bm25_results: List[Dict[str, Any]] = []
        try:
            bm25_results = self.bm25_retriever.bm25_search(
                query=query,
                top_k=bm25_top_k,
                filters=filters,
            )
        except Exception as e:
            logger.warning(f"BM25 retrieval error: {e}")

        # 3. Apply Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(
            ranked_lists=[dense_results, bm25_results],
            k=self.rrf_k,
            top_k=top_k,
            id_key="cutoff_record_id",
        )

        # 4. Log detailed rankings for explainability & debugging
        logger.info(f"Hybrid Fusion: Dense ({len(dense_results)}) + BM25 ({len(bm25_results)}) -> Top {len(fused)} results.")
        for r in fused[:5]:
            meta = r.get("metadata", {})
            logger.debug(
                f"Rank #{r.get('final_rank')}: {meta.get('college_code')} - {meta.get('course_name')} "
                f"({meta.get('category')}) | RRF: {r.get('rrf_score')} | Sources: {r.get('source_ranks')}"
            )

        return {
            "query": query,
            "fused_results": fused,
            "dense_results": dense_results,
            "bm25_results": bm25_results,
            "metadata": {
                "dense_count": len(dense_results),
                "bm25_count": len(bm25_results),
                "fused_count": len(fused),
                "rrf_k": self.rrf_k,
            },
        }


_hybrid_retriever: Optional[HybridRetriever] = None


def get_hybrid_retriever() -> HybridRetriever:
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever


def hybrid_search(
    query: str,
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    retriever = get_hybrid_retriever()
    return retriever.hybrid_search(query=query, top_k=top_k, filters=filters)

