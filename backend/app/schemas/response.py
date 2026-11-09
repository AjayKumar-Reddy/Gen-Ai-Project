from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CutoffRecordItem(BaseModel):
    id: Optional[int] = None
    college_code: str
    college_name: str
    location: Optional[str] = None
    course_code: str
    course_name: str
    category: str
    closing_rank: Optional[int] = None
    year: int
    counselling_round: int
    seat_region: str
    page_number: int


class SourceReferenceItem(BaseModel):
    document: str
    page_number: int
    college_code: Optional[str] = None
    college_name: Optional[str] = None
    category: Optional[str] = None
    closing_rank: Optional[int] = None


class RetrievalMetadata(BaseModel):
    dense_results: int = 0
    bm25_results: int = 0
    hybrid_results: int = 0
    student_rank_applied: Optional[int] = None
    category_applied: Optional[str] = None
    branch_applied: Optional[str] = None
    sql_matches: int = 0
    pipeline_steps: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    evidence_status: str
    results: List[Dict[str, Any]] = Field(default_factory=list)
    colleges: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    retrieval_metadata: RetrievalMetadata
    retrieval_method: str = "Hybrid (Dense pgvector + BM25 RRF)"
    query_type: str = "factual_cutoff"
    disclaimer: str = (
        "Historical KCET cutoffs for informational purposes only. "
        "Official seat allotment and counselling is conducted exclusively by KEA."
    )


class StatsResponse(BaseModel):
    dataset_year: int
    total_cutoff_combinations: int
    non_null_cutoffs: int
    college_count: int
    total_cutoff_records: Optional[int] = None
    total_colleges: Optional[int] = None
    embedding_model: Optional[str] = "gemini-embedding-001"
    llm_model: Optional[str] = "gemini-3.5-flash-lite"
    pgvector_dimension: Optional[int] = 768
    available_categories: List[str] = Field(default_factory=list)
    available_branches: List[Dict[str, str]] = Field(default_factory=list)
    available_rounds: List[int] = Field(default_factory=list)
    available_seat_regions: List[str] = Field(default_factory=list)

