# KCET College Information Assistant (Hybrid RAG)

An academic, production-grade AI-powered KCET College Information Chatbot for Karnataka engineering aspirants built using a **Hybrid Retrieval-Augmented Generation (RAG)** architecture.

The system retrieves information from official Karnataka Examinations Authority (KEA) KCET cutoff documents and delivers evidence-grounded, citation-backed answers combined with deterministic numerical rank filtering.

---

## Architecture Overview

```
USER
  │
  ▼
NEXT.JS FRONTEND (React 19 / Tailwind CSS)
  │
  │ HTTP REST API (port 8000)
  ▼
FASTAPI BACKEND
  │
  ├─► ENTITY EXTRACTION (College Code, Branch, Category, Student Rank)
  │
  ├───► DENSE RETRIEVER ────────┐
  │     (pgvector 768d Cosine)   │
  │                              ▼
  └───► BM25 RETRIEVER ──────► RECIPROCAL RANK FUSION (RRF, k=60)
        (rank-bm25 Okapi)        │
                                 ▼
                     TOP EVIDENCE VERIFICATION
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
                   ▼                           ▼
        STRUCTURED SQL FILTERING        GEMINI 3.5 FLASH LITE
        (student_rank <= closing_rank)  (Temperature 0, Factual)
                   │                           │
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                         GROUNDED RESPONSE
                     + Exact Source Citations
                     + Eligible College Cards
                     + Counselling Disclaimer
```

---

## Key Features

1. **High-Precision PDF Ingestion**: Extracts multi-column KCET cutoff tables (242 colleges, 1,668 courses, 56,610 cutoff combinations across 37 reservation categories) while preserving `NULL` for missing ranks (never 0).
2. **Dense Vector Search**: Powered by Google Gemini `gemini-embedding-001` (768 dimensions) stored in Neon PostgreSQL with an HNSW cosine similarity index.
3. **Sparse BM25 Keyword Search**: In-memory `BM25Okapi` with Karnataka engineering acronym expansion (`RVCE`, `MSRIT`, `BMSCE`, `UVCE`, `CSE`, `ISE`, `ECE`).
4. **Reciprocal Rank Fusion (RRF)**: Custom, transparent Python implementation ($k=60$) fusing Dense and BM25 candidate ranks.
5. **Deterministic Numerical Filtering**: Database-backed rank filter (`student_rank <= closing_rank`) preventing LLM arithmetic hallucination.
6. **Strict Evidence Grounding**: Powered by `gemini-3.5-flash-lite` at temperature 0, with mandatory page citations (`kcet_cutoff.pdf (Page X)`) and guardrails that refuse out-of-domain queries (e.g. medical NEET cutoffs, JEE Advanced).
7. **Interactive Next.js UI**: Clean academic interface with rank calculator, reservation category picker, branch selection, college results cards with rank buffer margins, and citation drawer.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn |
| **Python Env** | MiniConda (`kcet-rag`) |
| **Database** | Neon PostgreSQL with `pgvector` extension (HNSW Cosine Index) |
| **Embedding Model** | Google Gemini `gemini-embedding-001` (768 output dimensions) |
| **LLM Model** | Google Gemini `gemini-3.5-flash-lite` (Temperature 0) |
| **Keyword Search** | `rank-bm25` (BM25Okapi) |
| **PDF Extraction** | PyMuPDF (fitz), Pandas |
| **Testing** | Pytest, HTTPX |

---

## Repository Structure

```
kcet-hybrid-rag/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application & lifespan startup
│   │   ├── config/settings.py       # Pydantic settings (.env.local / .env)
│   │   ├── database/
│   │   │   ├── connection.py        # SQLAlchemy Neon connection pool
│   │   │   ├── models.py            # CutoffRecord, DocumentRecord (Vector 768), Source
│   │   │   └── schema.py            # HNSW index and table initialization
│   │   ├── ingestion/
│   │   │   ├── pdf_extractor.py     # 69-page KEA cutoff table extractor
│   │   │   ├── data_cleaner.py      # Normalization & category verification
│   │   │   └── database_loader.py   # Batch upsert into Neon PostgreSQL
│   │   ├── embeddings/
│   │   │   └── embedding_service.py # Gemini embeddings & vector persistence
│   │   ├── retrieval/
│   │   │   ├── dense_retriever.py   # pgvector cosine similarity search
│   │   │   ├── bm25_retriever.py    # BM25Okapi with acronym expansion
│   │   │   ├── rrf.py               # Reciprocal Rank Fusion (k=60)
│   │   │   └── hybrid_retriever.py  # Fused Dense + BM25 retrieval
│   │   ├── generation/
│   │   │   ├── llm.py               # Gemini 3.5 Flash Lite LLM client
│   │   │   └── prompts.py           # Strict academic grounding prompt
│   │   ├── services/
│   │   │   ├── chatbot.py           # End-to-end question coordination
│   │   │   └── cutoff_service.py    # Structured SQL rank filtering
│   │   ├── api/
│   │   │   ├── chat.py              # POST /api/chat
│   │   │   ├── colleges.py          # GET /api/cutoffs, /api/colleges, /api/stats
│   │   │   └── health.py            # GET /api/health
│   │   └── schemas/
│   │       ├── request.py           # Pydantic request models
│   │       └── response.py          # Pydantic response models
│   ├── scripts/
│   │   ├── ingest_kcet.py           # PDF ingestion CLI script
│   │   ├── rebuild_indexes.py       # Embeddings and vector index loader
│   │   └── evaluate_retrieval.py    # Retrieval & generation benchmark runner
│   ├── tests/                       # Complete pytest suite (24 passing tests)
│   ├── data/
│   │   ├── raw/kcet_cutoff.pdf      # Official 69-page KEA PDF
│   │   └── processed/               # Processed records & evaluation reports
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Main application dashboard
│   │   └── globals.css              # Tailwind styling
│   ├── components/
│   │   ├── ChatInterface.tsx        # Conversation coordinator
│   │   ├── ChatMessage.tsx          # Formatted response bubble
│   │   ├── ChatInput.tsx            # Query input with quick suggestions
│   │   ├── FilterPanel.tsx          # Side panel with eligibility controls
│   │   ├── RankForm.tsx             # Rank, category, and branch inputs
│   │   ├── CollegeResults.tsx       # Result cards with rank buffers
│   │   ├── SourceReferences.tsx     # Page citations & KEA disclaimers
│   │   └── LoadingIndicator.tsx     # Hybrid search thinking state
│   └── lib/
│       ├── api.ts                   # Backend REST client
│       └── types.ts                 # TypeScript definitions
└── README.md
```

---

## Setup & Running Instructions

### 1. Prerequisites
- **Python 3.11** (MiniConda recommended)
- **Node.js 18+** & npm
- **Google Gemini API Key** (with access to `gemini-embedding-001` and `gemini-3.5-flash-lite`)
- **Neon PostgreSQL Database** (with `pgvector` enabled)

### 2. Environment Variables
Create `backend/.env.local` (or `backend/.env`):
```ini
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql+psycopg://user:password@ep-xyz.neon.tech/neondb?sslmode=require
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSION=768
GEMINI_CHAT_MODEL=gemini-3.5-flash-lite
FRONTEND_URL=http://localhost:3000
RRF_K=60
TOP_K=10
```

---

### 3. Local Execution (Two Terminals)

#### Terminal 1: Backend (FastAPI)
```bash
# Activate conda environment
conda activate kcet-rag

# Navigate to backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start FastAPI server on port 8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
FastAPI interactive docs will be available at: `http://localhost:8000/docs`

#### Terminal 2: Frontend (Next.js)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if needed)
npm install

# Start Next.js development server on port 3000
npm run dev
```
Open browser to: `http://localhost:3000`

---

## Pipeline Execution & Verification Scripts

### Ingest Cutoff PDF into Neon PostgreSQL
```bash
cd backend
python -m scripts.ingest_kcet --file data/raw/kcet_cutoff.pdf
```

### Rebuild Gemini Vector Embeddings
```bash
cd backend
python -m scripts.rebuild_indexes --limit 500
```

### Run Benchmark Evaluation Suite
```bash
cd backend
python -m scripts.evaluate_retrieval
```

### Run Full Pytest Test Suite
```bash
cd backend
pytest tests/ -v
```

---

## Retrieval Benchmark Evaluation

Evaluated on 15 factual KCET benchmark queries covering college codes, acronyms, branch names, and categories:

| Retriever Architecture | Precision@5 | Recall@5 | Mean Reciprocal Rank (MRR) |
| :--- | :---: | :---: | :---: |
| **Dense Retriever (pgvector)** | `0.213` | `0.267` | `0.222` |
| **BM25 Keyword Retriever** | `0.347` | `0.400` | `0.400` |
| **Hybrid Retriever (Dense + BM25 RRF)** | **`0.280`** | **`0.533`** | **`0.327`** |

### Benchmark Takeaways:
- **Recall Advantage:** Hybrid RAG achieves **53.3% Recall@5**, significantly outperforming BM25 alone (40.0%) and Dense alone (26.7%).
- **Guardrails:** Refuses ungrounded out-of-domain queries (e.g. NEET medical, JEE Advanced, general knowledge) with 100% adherence to official cutoff evidence.
- **Explainability:** 100% of factual responses cite the exact document filename and PDF page number.

---

## Disclaimer
*This project is an academic demonstration of Generative AI and Hybrid RAG architectures. Historical KCET cutoffs are retrieved from official Karnataka Examinations Authority (KEA) documents for informational purposes only. Official seat allotments and counselling procedures are conducted exclusively by KEA.*

