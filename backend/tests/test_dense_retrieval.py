import pytest
from app.retrieval.dense_retriever import DenseRetriever
from app.config.settings import get_settings


def test_dense_search_with_pgvector():
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        pytest.skip("GOOGLE_API_KEY not configured.")

    retriever = DenseRetriever()
    results = retriever.dense_search("RV College of Engineering Computer Science", top_k=5)

    assert len(results) > 0
    # Verify content and metadata are preserved
    top_doc = results[0]
    assert "content" in top_doc
    assert "metadata" in top_doc
    assert "score" in top_doc
    assert "dense_rank" in top_doc
    assert top_doc["score"] > 0.0

    # Verify metadata fields
    meta = top_doc["metadata"]
    assert "college_code" in meta
    assert "course_name" in meta
    assert "closing_rank" in meta
    assert "page_number" in meta

