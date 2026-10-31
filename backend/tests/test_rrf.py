import pytest
from app.retrieval.rrf import reciprocal_rank_fusion


def test_rrf_mathematical_calculation():
    # doc A: rank 1 in list 1 (score = 1 / (60 + 1) = 1/61 = 0.016393)
    # doc B: rank 2 in list 1 (score = 1 / (60 + 2) = 1/62 = 0.016129)
    # doc A: rank 2 in list 2 (score = 1 / (60 + 2) = 1/62 = 0.016129)
    # Total for doc A = 1/61 + 1/62 = 0.032522
    # doc C: rank 1 in list 2 (score = 1/61 = 0.016393)

    list1 = [
        {"cutoff_record_id": 10, "content": "Doc A", "source": "dense"},
        {"cutoff_record_id": 20, "content": "Doc B", "source": "dense"},
    ]
    list2 = [
        {"cutoff_record_id": 30, "content": "Doc C", "source": "bm25"},
        {"cutoff_record_id": 10, "content": "Doc A", "source": "bm25"},
    ]

    fused = reciprocal_rank_fusion([list1, list2], k=60, top_k=5)

    assert len(fused) == 3
    # Doc A should be rank 1 because it appeared in both lists
    assert fused[0]["cutoff_record_id"] == 10
    assert fused[0]["final_rank"] == 1
    # Check score precision
    expected_score_a = round(1.0 / 61 + 1.0 / 62, 6)
    assert fused[0]["rrf_score"] == expected_score_a

    # Check rank tracking in source_ranks
    assert fused[0]["source_ranks"]["dense_rank"] == 1
    assert fused[0]["source_ranks"]["bm25_rank"] == 2


def test_rrf_duplicate_handling_and_ordering():
    # Test that duplicate documents in both lists are merged seamlessly
    list1 = [{"cutoff_record_id": i, "content": f"Doc {i}", "source": "dense"} for i in range(1, 6)]
    list2 = [{"cutoff_record_id": i, "content": f"Doc {i}", "source": "bm25"} for i in range(3, 8)]

    fused = reciprocal_rank_fusion([list1, list2], k=60, top_k=10)

    # Document IDs 3, 4, 5 appear in both lists and must have higher scores than single-list appearances
    top_3_ids = [f["cutoff_record_id"] for f in fused[:3]]
    assert set(top_3_ids) == {3, 4, 5}
    assert fused[0]["cutoff_record_id"] == 3  # rank 3 in list1 + rank 1 in list2

    # Verify no duplicate IDs in fused results
    seen_ids = [f["cutoff_record_id"] for f in fused]
    assert len(seen_ids) == len(set(seen_ids))


def test_rrf_empty_lists():
    assert reciprocal_rank_fusion([], k=60) == []
    assert reciprocal_rank_fusion([[]], k=60) == []

