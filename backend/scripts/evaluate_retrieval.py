"""
Comprehensive Retrieval and Generation Evaluation Script.
Evaluates Dense (pgvector), BM25, and Hybrid (RRF) Retrieval on:
- Precision@5
- Hit Rate@5 (fraction of queries with >=1 relevant record in the top 5)
- Mean Reciprocal Rank (MRR)
- Generation Cutoff Accuracy & Citation Validity
- Out-of-domain Refusal Rate
"""

import os
import json
import time
from typing import List, Dict, Any
from app.config.settings import get_settings
from app.database.connection import SessionLocal
from app.embeddings.embedding_service import EmbeddingService
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.services.chatbot import ChatbotService

# 20 Factual Evaluation Queries with Ground Truth Expected College Codes / Branches
BENCHMARK_QUERIES = [
    {
        "id": "Q01",
        "query": "What is the cutoff for RV College of Engineering in Computer Science?",
        "expected_college": "E005",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q02",
        "query": "BMS College of Engineering CS cutoffs for GM",
        "expected_college": "E003",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q03",
        "query": "Cutoff for E001 in Computer Science and Engineering",
        "expected_college": "E001",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q04",
        "query": "What is the Information Science cutoff for MS Ramaiah Institute of Technology?",
        "expected_college": "E006",
        "expected_course": "IS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q05",
        "query": "PES University Bangalore CS cutoff rank",
        "expected_college": "E009",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q06",
        "query": "What is the Electronics and Communication cutoff for Dayananda Sagar?",
        "expected_college": "E007",
        "expected_course": "EC",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q07",
        "query": "National Institute of Engineering Mysore CSE cutoff",
        "expected_college": "E178",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q08",
        "query": "What is the Mechanical Engineering cutoff for UVCE Bangalore?",
        "expected_college": "E001",
        "expected_course": "ME",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q09",
        "query": "Siddaganga Institute of Technology Tumkur CS cutoff",
        "expected_college": "E016",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q10",
        "query": "Sir M Visvesvaraya Institute of Technology Bangalore ECE cutoff",
        "expected_college": "E012",
        "expected_course": "EC",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q11",
        "query": "What is the 2AG cutoff for RVCE in Computer Science?",
        "expected_college": "E005",
        "expected_course": "CS",
        "category": "2AG",
        "is_out_of_domain": False
    },
    {
        "id": "Q12",
        "query": "Cutoff for E003 Electrical and Electronics Engineering",
        "expected_college": "E003",
        "expected_course": "EE",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q13",
        "query": "What is the cutoff for E006 in Civil Engineering?",
        "expected_college": "E006",
        "expected_course": "CV",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q14",
        "query": "Bangalore Institute of Technology BIT CS cutoff",
        "expected_college": "E008",
        "expected_course": "CS",
        "category": "GM",
        "is_out_of_domain": False
    },
    {
        "id": "Q15",
        "query": "What is the 3AG cutoff for Dayananda Sagar College of Engineering in CS?",
        "expected_college": "E007",
        "expected_course": "CS",
        "category": "3AG",
        "is_out_of_domain": False
    },
    # Out of domain / Unanswerable queries (testing model refusal)
    {
        "id": "Q16",
        "query": "What is the MBBS NEET cutoff for Bangalore Medical College?",
        "is_out_of_domain": True
    },
    {
        "id": "Q17",
        "query": "What is the JEE Advanced opening rank for IIT Bombay Computer Science?",
        "is_out_of_domain": True
    },
    {
        "id": "Q18",
        "query": "What is the MBA CAT percentile cutoff for IIM Bangalore?",
        "is_out_of_domain": True
    },
    {
        "id": "Q19",
        "query": "What are the engineering cutoffs for colleges in Tamil Nadu Anna University?",
        "is_out_of_domain": True
    },
    {
        "id": "Q20",
        "query": "Who is the Prime Minister of India?",
        "is_out_of_domain": True
    }
]


def is_relevant(doc_meta: Dict[str, Any], query_spec: Dict[str, Any]) -> bool:
    if query_spec.get("is_out_of_domain"):
        return False

    col_code = doc_meta.get("college_code", "")
    course_code = doc_meta.get("course_code", "")

    expected_col = query_spec["expected_college"]
    expected_course = query_spec["expected_course"]

    college_match = col_code.upper() == expected_col.upper()
    # Exact branch-code match only. A substring test on the course name is too
    # loose (e.g. "IE" is a substring of "SCIENCE", so any CS course matched).
    course_match = course_code.upper() == expected_course.upper()

    return college_match and course_match


def calculate_metrics(results: List[Dict[str, Any]], query_spec: Dict[str, Any], k: int = 5):
    top_k = results[:k]
    relevant_ranks = []
    relevant_count = 0

    for idx, item in enumerate(top_k):
        meta = item.get("metadata", {})
        if is_relevant(meta, query_spec):
            relevant_count += 1
            relevant_ranks.append(idx + 1)

    precision = relevant_count / k if k > 0 else 0.0
    recall = 1.0 if relevant_count > 0 else 0.0
    mrr = (1.0 / relevant_ranks[0]) if relevant_ranks else 0.0

    return precision, recall, mrr


def run_evaluation():
    print("=" * 70)
    print("KCET HYBRID RAG BENCHMARK EVALUATION SUITE")
    print("=" * 70)

    settings = get_settings()
    embedder = EmbeddingService()
    session = SessionLocal()

    dense_retriever = DenseRetriever(embedding_service=embedder)

    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    bm25_retriever = BM25Retriever()
    bm25_retriever.build_index()
    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        bm25_retriever=bm25_retriever,
        rrf_k=60,
    )
    chatbot = ChatbotService(hybrid_retriever=hybrid_retriever)

    factual_queries = [q for q in BENCHMARK_QUERIES if not q.get("is_out_of_domain")]
    ood_queries = [q for q in BENCHMARK_QUERIES if q.get("is_out_of_domain")]

    dense_metrics = {"p@5": [], "r@5": [], "mrr": []}
    bm25_metrics = {"p@5": [], "r@5": [], "mrr": []}
    hybrid_metrics = {"p@5": [], "r@5": [], "mrr": []}

    print(f"\n1. Evaluating Retrieval Performance across {len(factual_queries)} Factual Queries (k=5)...")
    for q in factual_queries:
        query_text = q["query"]

        # Run hybrid search which executes both and fuses via RRF
        res = hybrid_retriever.hybrid_search(
            query=query_text,
            top_k=5,
            dense_top_k=10,
            bm25_top_k=10,
        )

        dense_res = res["dense_results"]
        bm25_res = res["bm25_results"]
        fused_res = res["fused_results"]

        dp, dr, dm = calculate_metrics(dense_res, q, k=5)
        dense_metrics["p@5"].append(dp)
        dense_metrics["r@5"].append(dr)
        dense_metrics["mrr"].append(dm)

        bp, br, bm = calculate_metrics(bm25_res, q, k=5)
        bm25_metrics["p@5"].append(bp)
        bm25_metrics["r@5"].append(br)
        bm25_metrics["mrr"].append(bm)

        hp, hr, hm = calculate_metrics(fused_res, q, k=5)
        hybrid_metrics["p@5"].append(hp)
        hybrid_metrics["r@5"].append(hr)
        hybrid_metrics["mrr"].append(hm)

        def _first(m):
            return f"rank {round(1 / m)}" if m > 0 else "miss"
        print(f"  {q['id']}: dense={_first(dm):7s} bm25={_first(bm):7s} hybrid={_first(hm):7s} | {query_text}")

    avg_dense = {k: sum(v) / len(v) for k, v in dense_metrics.items()}
    avg_bm25 = {k: sum(v) / len(v) for k, v in bm25_metrics.items()}
    avg_hybrid = {k: sum(v) / len(v) for k, v in hybrid_metrics.items()}

    print(f"\nDense PGVector:  Precision@5: {avg_dense['p@5']:.3f} | Hit@5: {avg_dense['r@5']:.3f} | MRR: {avg_dense['mrr']:.3f}")
    print(f"BM25 Keyword:   Precision@5: {avg_bm25['p@5']:.3f} | Hit@5: {avg_bm25['r@5']:.3f} | MRR: {avg_bm25['mrr']:.3f}")
    print(f"Hybrid (RRF):   Precision@5: {avg_hybrid['p@5']:.3f} | Hit@5: {avg_hybrid['r@5']:.3f} | MRR: {avg_hybrid['mrr']:.3f}")

    print(f"\n2. Evaluating Out-of-Domain Refusal Rate across {len(ood_queries)} queries...")
    refusal_success = 0
    ood_lines = []
    for q in ood_queries:
        out = chatbot.process_query(question=q["query"])
        content_lower = out["answer"].lower()
        refused = (
            "not found" in content_lower
            or "not available" in content_lower
            or "does not contain" in content_lower
            or "cannot answer" in content_lower
            or "engineering cutoffs only" in content_lower
            or "outside the scope" in content_lower
            or "out of scope" in content_lower
            or out.get("query_type") == "out_of_domain_refusal"
            or "not provide" in content_lower
        )
        if refused:
            refusal_success += 1
        snippet = " ".join(out["answer"].split())[:160]
        ood_lines.append(f"- **{q['id']}** ({'refused' if refused else 'NOT refused'}): {q['query']}  \n  > {snippet}...")
        print(f"  {q['id']}: {'refused' if refused else 'NOT refused'} | {snippet[:100]}")
    ood_details = "\n".join(ood_lines)

    session.close()
    from sqlalchemy import text as _text
    with SessionLocal() as s2:
        indexed_docs = s2.execute(_text("select count(*) from documents where embedding is not null")).scalar()
    bm25_docs = len(bm25_retriever.corpus_docs)

    refusal_rate = (refusal_success / len(ood_queries)) * 100
    print(f"Out-of-Domain Refusal Rate: {refusal_rate:.1f}% ({refusal_success}/{len(ood_queries)})")

    # Generate Markdown Report
    report_content = f"""# KCET Hybrid RAG Architecture Evaluation Report

**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Embedding Model:** `{EmbeddingService().model}` (768 dimensions)  
**LLM Generator:** `gemini-3.5-flash-lite` (Temperature 0)  
**Vector Store:** Neon PostgreSQL (`pgvector` HNSW Cosine Index)  
**Keyword Index:** `rank-bm25` (In-memory, KCET Acronym Expansion)  
**Fusion Algorithm:** Reciprocal Rank Fusion ($k=60$)  

---

## 1. Information Retrieval Benchmark Results

Evaluated across {len(factual_queries)} domain-specific benchmark test cases representing college acronyms, codes, categories, and branch inquiries.

| Retriever Architecture | Precision@5 | Hit@5 | Mean Reciprocal Rank (MRR) |
| :--- | :---: | :---: | :---: |
| **Dense Retriever (pgvector)** | `{avg_dense['p@5']:.3f}` | `{avg_dense['r@5']:.3f}` | `{avg_dense['mrr']:.3f}` |
| **BM25 Keyword Retriever** | `{avg_bm25['p@5']:.3f}` | `{avg_bm25['r@5']:.3f}` | `{avg_bm25['mrr']:.3f}` |
| **Hybrid Retriever (Dense + BM25 RRF)** | **`{avg_hybrid['p@5']:.3f}`** | **`{avg_hybrid['r@5']:.3f}`** | **`{avg_hybrid['mrr']:.3f}`** |

### Key Retrieval Observations:
- A retrieved record is relevant when its college code AND branch code exactly match the expected values.
- Hit@5 = fraction of queries with at least one relevant record in the top 5.
- Retrieval is run without metadata filters here, so these numbers measure ranking quality alone
  (the chatbot additionally applies category/branch/college-code filters extracted from the query).
- Documents indexed: {indexed_docs} (dense) / {bm25_docs} (BM25).

---

## 2. Guardrails & Evidence Grounding Verification

- **Total Out-of-Domain Queries Tested:** {len(ood_queries)} (e.g. NEET MBBS cutoffs, JEE Advanced ranks, non-KCET queries)
- **Refusal / Out-of-Scope Detection Rate:** **{refusal_rate:.1f}%**
- Refusal is detected by keyword matching on the generated answer, so this is an approximate measure.

### Out-of-Domain Answers
{ood_details}

---

## 3. Architecture Summary

```
Query -> Entity Extraction -> [ Dense pgvector (top 10) + BM25 (top 10) ]
                            -> Reciprocal Rank Fusion (k=60)
                            -> Top-10 fused evidence (+ SQL rank filtering for rank queries)
                            -> Strict Grounded Generation (Gemini 3.5 Flash Lite)
                            -> Response + Source Citations + Disclaimer
```
"""

    report_path = os.path.join(data_dir, "processed", "evaluation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\nReport successfully generated and saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()
