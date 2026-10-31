import logging
from fastapi import APIRouter, HTTPException
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse, RetrievalMetadata
from app.services.chatbot import get_chatbot_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main Chat API endpoint.
    Performs Hybrid RAG (Dense pgvector + BM25 + RRF) and structured rank filtering,
    followed by evidence-grounded generation with Google Gemini.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        service = get_chatbot_service()
        result = service.process_query(
            question=request.question,
            student_rank=request.student_rank,
            category=request.category,
            branch=request.branch,
            counselling_round=request.round,
            seat_region=request.seat_region,
            session_id=request.session_id,
        )

        meta = result.get("retrieval_metadata", {})
        raw_results = result.get("results", [])
        student_rank = meta.get("student_rank_applied")
        query_type = "rank_filter" if (student_rank is not None and student_rank > 0) else "factual_cutoff"

        # Format college options with consistent keys for frontend CollegeResults component
        formatted_colleges = []
        for r in raw_results:
            if isinstance(r, dict):
                formatted_colleges.append({
                    "college_code": r.get("college_code", ""),
                    "college_name": r.get("college_name", ""),
                    "location": r.get("location"),
                    "course_code": r.get("course_code", ""),
                    "course_name": r.get("course_name", ""),
                    "category": r.get("category", request.category),
                    "closing_rank": r.get("closing_rank") or 0,
                    "round": r.get("counselling_round", request.round),
                    "region": r.get("seat_region", request.seat_region),
                    "page_number": r.get("page_number", 1),
                })

        # Format sources with consistent keys for frontend SourceReferences component
        formatted_sources = []
        for s in result.get("sources", []):
            if isinstance(s, dict):
                formatted_sources.append({
                    "college_code": s.get("college_code", ""),
                    "college_name": s.get("college_name", ""),
                    "course_code": s.get("course_code", ""),
                    "course_name": s.get("course_name", ""),
                    "category": s.get("category", request.category),
                    "closing_rank": s.get("closing_rank"),
                    "page_number": s.get("page_number", 1),
                    "filename": s.get("filename", "kcet_cutoff.pdf"),
                    "round": s.get("round", request.round),
                    "region": s.get("region", request.seat_region),
                })

        return ChatResponse(
            answer=result["answer"],
            evidence_status=result["evidence_status"],
            results=raw_results,
            colleges=formatted_colleges,
            sources=formatted_sources,
            retrieval_metadata=RetrievalMetadata(
                dense_results=meta.get("dense_results", 0),
                bm25_results=meta.get("bm25_results", 0),
                hybrid_results=meta.get("hybrid_results", 0),
                student_rank_applied=meta.get("student_rank_applied"),
                category_applied=meta.get("category_applied"),
                branch_applied=meta.get("branch_applied"),
            ),
            retrieval_method="Hybrid (Dense pgvector + BM25 RRF)",
            query_type=query_type,
            disclaimer=(
                "Historical KCET cutoffs for informational purposes only. "
                "Official seat allotment and counselling is conducted exclusively by KEA."
            ),
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

