import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.connection import get_db
from app.database.models import CutoffRecord
from app.schemas.response import StatsResponse
from app.services.cutoff_service import CutoffService
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api", tags=["Colleges & Cutoffs"])


@router.get("/colleges")
def list_colleges(
    college_name: Optional[str] = Query(None, description="Filter by college name substring"),
    college_code: Optional[str] = Query(None, description="Filter by exact college code (e.g. E005)"),
    branch: Optional[str] = Query(None, description="Filter by branch / course code (e.g. CS)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. GM, 2AG)"),
    rank: Optional[int] = Query(None, description="Student rank (filters closing_rank >= rank)"),
    min_rank: Optional[int] = Query(None, description="Minimum cutoff rank for range filtering"),
    max_rank: Optional[int] = Query(None, description="Maximum cutoff rank for range filtering"),
    year: Optional[int] = Query(None, description="Examination year (e.g. 2026)"),
    round: int = Query(1, description="Counselling round"),
    seat_region: str = Query("Rest of Karnataka", description="Seat region"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """
    Search and filter KCET colleges and cutoff records.
    """
    try:
        query = db.query(CutoffRecord).filter(
            CutoffRecord.counselling_round == round,
            CutoffRecord.seat_region == seat_region,
            CutoffRecord.closing_rank.isnot(None),
        )

        if rank is not None and rank > 0:
            query = query.filter(CutoffRecord.closing_rank >= rank)
        if min_rank is not None and min_rank > 0:
            query = query.filter(CutoffRecord.closing_rank >= min_rank)
        if max_rank is not None and max_rank > 0:
            query = query.filter(CutoffRecord.closing_rank <= max_rank)
        if year is not None:
            query = query.filter(CutoffRecord.year == year)

        if college_code:
            query = query.filter(CutoffRecord.college_code == college_code.strip().upper())
        if college_name:
            query = query.filter(CutoffRecord.college_name.ilike(f"%{college_name.strip()}%"))
        if branch:
            b_clean = branch.strip().upper()
            if len(b_clean) <= 3:
                query = query.filter(CutoffRecord.course_code == b_clean)
            else:
                query = query.filter(
                    or_(
                        CutoffRecord.course_code == b_clean,
                        CutoffRecord.course_name.ilike(f"%{b_clean}%"),
                    )
                )
        if category:
            query = query.filter(CutoffRecord.category == category.strip().upper())

        records = query.order_by(CutoffRecord.closing_rank.asc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "college_code": r.college_code,
                "college_name": r.college_name,
                "location": r.location,
                "course_code": r.course_code,
                "course_name": r.course_name,
                "category": r.category,
                "closing_rank": r.closing_rank,
                "year": r.year,
                "counselling_round": r.counselling_round,
                "seat_region": r.seat_region,
                "page_number": r.page_number,
            }
            for r in records
        ]
    except Exception as e:
        logger.error(f"Error querying colleges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cutoffs")
def get_cutoffs(
    college_code: str = Query(..., description="College code (e.g. E005)"),
    category: str = Query("GM", description="Reservation category"),
    course_code: Optional[str] = Query(None, description="Course code (e.g. CS)"),
    round: int = Query(1, description="Counselling round"),
    seat_region: str = Query("Rest of Karnataka", description="Seat region"),
    db: Session = Depends(get_db),
):
    """
    Exact structured cutoff lookup by college code and category.
    """
    try:
        service = CutoffService(db=db)
        cutoffs = service.get_exact_cutoff(
            college_code=college_code,
            category=category,
            course_code=course_code,
            counselling_round=round,
            seat_region=seat_region,
        )
        return cutoffs
    except Exception as e:
        logger.error(f"Error looking up cutoffs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics and distribution of the loaded KCET dataset.
    """
    try:
        service = CutoffService(db=db)
        stats = service.get_dataset_statistics()
        stats["total_cutoff_records"] = stats.get("total_cutoff_combinations", 0)
        stats["total_colleges"] = stats.get("college_count", 0)
        stats["embedding_model"] = settings.GEMINI_EMBEDDING_MODEL
        stats["llm_model"] = settings.GEMINI_CHAT_MODEL
        stats["pgvector_dimension"] = settings.EMBEDDING_DIMENSION
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
