# KCET Hybrid RAG Architecture Evaluation Report

**Date:** 2026-11-17 20:54:03  
**Embedding Model:** `BAAI/bge-base-en-v1.5` (768 dimensions)  
**LLM Generator:** `gemini-3.5-flash-lite` (Temperature 0)  
**Vector Store:** Neon PostgreSQL (`pgvector` HNSW Cosine Index)  
**Keyword Index:** `rank-bm25` (In-memory, KCET Acronym Expansion)  
**Fusion Algorithm:** Reciprocal Rank Fusion ($k=60$)  

---

## 1. Information Retrieval Benchmark Results

Evaluated across 15 domain-specific benchmark test cases representing college acronyms, codes, categories, and branch inquiries.

| Retriever Architecture | Precision@5 | Hit@5 | Mean Reciprocal Rank (MRR) |
| :--- | :---: | :---: | :---: |
| **Dense Retriever (pgvector)** | `0.320` | `0.400` | `0.306` |
| **BM25 Keyword Retriever** | `0.493` | `0.600` | `0.556` |
| **Hybrid Retriever (Dense + BM25 RRF)** | **`0.427`** | **`0.667`** | **`0.580`** |

### Key Retrieval Observations:
- A retrieved record is relevant when its college code AND branch code exactly match the expected values.
- Hit@5 = fraction of queries with at least one relevant record in the top 5.
- Retrieval is run without metadata filters here, so these numbers measure ranking quality alone
  (the chatbot additionally applies category/branch/college-code filters extracted from the query).
- Documents indexed: 11426 (dense) / 20978 (BM25).

---

## 2. Guardrails & Evidence Grounding Verification

- **Total Out-of-Domain Queries Tested:** 5 (e.g. NEET MBBS cutoffs, JEE Advanced ranks, non-KCET queries)
- **Refusal / Out-of-Scope Detection Rate:** **100.0%**
- Refusal is detected by keyword matching on the generated answer, so this is an approximate measure.

### Out-of-Domain Answers
- **Q16** (refused): What is the MBBS NEET cutoff for Bangalore Medical College?  
  > The question about the MBBS NEET cutoff for Bangalore Medical College is outside the scope of this assistant, which only covers Karnataka KCET engineering cutof...
- **Q17** (refused): What is the JEE Advanced opening rank for IIT Bombay Computer Science?  
  > The question about JEE Advanced opening ranks for IIT Bombay Computer Science is outside the scope of this assistant, which only covers Karnataka KCET engineeri...
- **Q18** (refused): What is the MBA CAT percentile cutoff for IIM Bangalore?  
  > This question is outside the scope of this assistant, which only covers KCET engineering cutoffs....
- **Q19** (refused): What are the engineering cutoffs for colleges in Tamil Nadu Anna University?  
  > This question is outside the scope of this assistant, which only covers Karnataka KCET engineering cutoffs....
- **Q20** (refused): Who is the Prime Minister of India?  
  > That question is outside the scope of this assistant, which only covers KCET engineering cutoffs....

---

## 3. Architecture Summary

```
Query -> Entity Extraction -> [ Dense pgvector (top 10) + BM25 (top 10) ]
                            -> Reciprocal Rank Fusion (k=60)
                            -> Top-10 fused evidence (+ SQL rank filtering for rank queries)
                            -> Strict Grounded Generation (Gemini 3.5 Flash Lite)
                            -> Response + Source Citations + Disclaimer
```
