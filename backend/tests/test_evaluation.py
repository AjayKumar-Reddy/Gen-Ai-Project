"""
Test Suite for Retrieval Metrics & Fusion Evaluation (Section 17.H & 17.I)
"""

import pytest
from app.retrieval.rrf import reciprocal_rank_fusion


def test_rrf_scoring_and_ranking():
    """Verify that Reciprocal Rank Fusion computes correct 1 / (k + rank) scores."""
    list1 = [
        {"cutoff_record_id": 101, "name": "Item A"},
        {"cutoff_record_id": 102, "name": "Item B"},
        {"cutoff_record_id": 103, "name": "Item C"},
    ]
    list2 = [
        {"cutoff_record_id": 102, "name": "Item B"},
        {"cutoff_record_id": 101, "name": "Item A"},
        {"cutoff_record_id": 104, "name": "Item D"},
    ]

    fused = reciprocal_rank_fusion(
        ranked_lists=[list1, list2],
        k=60,
        top_k=4,
        id_key="cutoff_record_id",
    )

    assert len(fused) == 4
    # Item A has rank 1 in list1 and rank 2 in list2: 1/61 + 1/62 = 0.016393 + 0.016129 = 0.032522
    # Item B has rank 2 in list1 and rank 1 in list2: 1/62 + 1/61 = 0.032522
    # Both Item A and Item B have identical maximum score (0.032522), much higher than Item C (1/63) or D (1/63)
    top_ids = {fused[0]["cutoff_record_id"], fused[1]["cutoff_record_id"]}
    assert top_ids == {101, 102}
    assert fused[0]["rrf_score"] > fused[2]["rrf_score"]
    assert fused[1]["rrf_score"] > fused[2]["rrf_score"]


def test_mrr_metric_calculation():
    """Verify Mean Reciprocal Rank formula."""
    from scripts.evaluate_retrieval import calculate_metrics

    query_spec = {
        "expected_college": "E005",
        "expected_course": "CS",
        "is_out_of_domain": False,
    }

    # Case 1: First item is relevant (MRR = 1.0)
    res_rank_1 = [
        {"metadata": {"college_code": "E005", "course_code": "CS", "course_name": "Computer Science"}},
        {"metadata": {"college_code": "E003", "course_code": "CS", "course_name": "Computer Science"}},
    ]
    p, r, mrr = calculate_metrics(res_rank_1, query_spec, k=5)
    assert mrr == 1.0
    assert r == 1.0
    assert p == 0.2

    # Case 2: Second item is relevant (MRR = 0.5)
    res_rank_2 = [
        {"metadata": {"college_code": "E001", "course_code": "ME", "course_name": "Mechanical"}},
        {"metadata": {"college_code": "E005", "course_code": "CS", "course_name": "Computer Science"}},
    ]
    p, r, mrr = calculate_metrics(res_rank_2, query_spec, k=5)
    assert mrr == 0.5
    assert r == 1.0
    assert p == 0.2

    # Case 3: No relevant item (MRR = 0.0)
    res_none = [
        {"metadata": {"college_code": "E001", "course_code": "ME", "course_name": "Mechanical"}},
    ]
    p, r, mrr = calculate_metrics(res_none, query_spec, k=5)
    assert mrr == 0.0
    assert r == 0.0
    assert p == 0.0

