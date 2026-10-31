import pytest
from app.retrieval.bm25_retriever import BM25Retriever, bm25_tokenize


def test_bm25_tokenization():
    text = "College Code: E005, RV College of Engineering. Course: CS, Category: GM, Rank: 425"
    tokens = bm25_tokenize(text)
    assert "e005" in tokens or "E005" in tokens
    assert "cs" in tokens or "CS" in tokens
    assert "gm" in tokens or "GM" in tokens
    assert "425" in tokens
    assert "engineering" in tokens


def test_bm25_exact_matches():
    retriever = BM25Retriever()
    retriever.build_index()

    # 1. Exact college code search
    results_code = retriever.bm25_search("E005", top_k=5)
    assert len(results_code) > 0
    assert any(r["metadata"]["college_code"] == "E005" for r in results_code)

    # 2. Exact college name and course
    results_name = retriever.bm25_search("RV College of Engineering Computer Science", top_k=5)
    assert len(results_name) > 0
    assert any("R. V. College of Engineering" in r["metadata"]["college_name"] for r in results_name)

    # 3. Category match
    results_cat = retriever.bm25_search("E001 Computer Science GM", top_k=5)
    assert len(results_cat) > 0
    assert any(r["metadata"]["college_code"] == "E001" and r["metadata"]["category"] == "GM" for r in results_cat)

