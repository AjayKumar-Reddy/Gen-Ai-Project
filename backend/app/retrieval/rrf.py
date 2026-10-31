import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    k: int = 60,
    top_k: int = 10,
    id_key: str = "cutoff_record_id",
) -> List[Dict[str, Any]]:
    """
    Combines multiple ranked document lists into a single ranked list using
    Reciprocal Rank Fusion (RRF).

    Formula:
        RRF_score(d) = sum_{list in ranked_lists} ( 1 / (k + rank_{list}(d)) )

    Args:
        ranked_lists: A list of ranked document lists, where each list contains
                      documents in rank order (rank starting at 1).
        k: The RRF smoothing constant (default: 60).
        top_k: Number of fused results to return.
        id_key: Key in document dictionary representing the unique document identifier.

    Returns:
        List of fused document dictionaries sorted by descending RRF score,
        with rank details preserved.
    """
    rrf_scores: Dict[Any, float] = {}
    doc_registry: Dict[Any, Dict[str, Any]] = {}
    rank_details: Dict[Any, Dict[str, int]] = {}

    for list_idx, doc_list in enumerate(ranked_lists):
        source_name = f"list_{list_idx}"
        for rank, doc in enumerate(doc_list, start=1):
            doc_id = doc.get(id_key) or doc.get("id")
            if doc_id is None:
                continue

            # Determine source label
            item_source = doc.get("source", source_name)

            # Accumulate reciprocal rank score
            score_increment = 1.0 / (k + rank)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + score_increment

            # Register document metadata
            if doc_id not in doc_registry:
                doc_registry[doc_id] = doc.copy()
                rank_details[doc_id] = {}

            rank_details[doc_id][f"{item_source}_rank"] = rank

    # Sort documents by accumulated RRF score descending
    sorted_doc_ids = sorted(
        rrf_scores.keys(), key=lambda d_id: rrf_scores[d_id], reverse=True
    )

    fused_results: List[Dict[str, Any]] = []
    for final_rank, doc_id in enumerate(sorted_doc_ids[:top_k], start=1):
        doc = doc_registry[doc_id]
        doc["rrf_score"] = round(rrf_scores[doc_id], 6)
        doc["final_rank"] = final_rank
        doc["source_ranks"] = rank_details[doc_id]
        fused_results.append(doc)

    logger.debug(
        f"RRF fused {sum(len(l) for l in ranked_lists)} input items into "
        f"{len(fused_results)} unique top documents (k={k})."
    )
    return fused_results

