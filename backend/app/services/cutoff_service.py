import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import CutoffRecord
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CutoffService:
    """
    Service for exact, deterministic numerical filtering and structured queries
    over KCET cutoff records in Neon PostgreSQL.
    """

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def get_db(self) -> Session:
        if self._db is not None:
            return self._db
        if SessionLocal is None:
            raise RuntimeError("Database connection not configured.")
        return SessionLocal()

    def filter_by_rank(
        self,
        student_rank: Optional[int] = None,
        min_rank: Optional[int] = None,
        max_rank: Optional[int] = None,
        category: str = "GM",
        branch: Optional[str] = None,
        counselling_round: int = 1,
        seat_region: str = "Rest of Karnataka",
        college_code: Optional[str] = None,
        college_name: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Execute deterministic structured SQL filtering over cutoff records.
        Supports both point eligibility filtering (student_rank <= closing_rank)
        and numerical rank range filtering (min_rank <= closing_rank <= max_rank).
        Excludes records with missing cutoff ranks (NULL).
        """
        db = self.get_db()
        should_close = self._db is None

        try:
            # Base query: non-null closing ranks, matching round and seat region
            query = db.query(CutoffRecord).filter(
                and_(
                    CutoffRecord.closing_rank.isnot(None),
                    CutoffRecord.counselling_round == counselling_round,
                    CutoffRecord.seat_region == seat_region,
                )
            )

            # Examination year filter
            if year:
                query = query.filter(CutoffRecord.year == year)

            # Reservation category filter (exact uppercase)
            if category:
                query = query.filter(CutoffRecord.category == category.upper())

            # Numerical Rank Conditions:
            # 1. Point eligibility (student_rank <= closing_rank)
            if student_rank is not None and student_rank > 0:
                query = query.filter(CutoffRecord.closing_rank >= student_rank)

            # 2. Rank Range queries (e.g. between min_rank and max_rank)
            if min_rank is not None and min_rank > 0:
                query = query.filter(CutoffRecord.closing_rank >= min_rank)
            if max_rank is not None and max_rank > 0:
                query = query.filter(CutoffRecord.closing_rank <= max_rank)

            # Engineering branch filter (matches course_code or course_name)
            if branch:
                clean_branch = branch.strip().upper()
                if len(clean_branch) <= 3:
                    query = query.filter(CutoffRecord.course_code == clean_branch)
                else:
                    query = query.filter(
                        or_(
                            CutoffRecord.course_code == clean_branch,
                            CutoffRecord.course_name.ilike(f"%{clean_branch}%"),
                        )
                    )

            # Optional college code filter
            if college_code:
                query = query.filter(CutoffRecord.college_code == college_code.strip().upper())

            # Optional college name filter
            if college_name:
                query = query.filter(CutoffRecord.college_name.ilike(f"%{college_name.strip()}%"))

            # Order by closing rank ascending (closest cutoffs first)
            query = query.order_by(CutoffRecord.closing_rank.asc()).limit(limit)

            records = query.all()
            results = []
            for r in records:
                results.append({
                    "id": r.id,
                    "college_code": r.college_code,
                    "college_name": r.college_name,
                    "location": r.location,
                    "course_code": r.course_code,
                    "course_name": r.course_name,
                    "category": r.category,
                    "closing_rank": r.closing_rank,
                    "student_rank": student_rank,
                    "year": r.year,
                    "counselling_round": r.counselling_round,
                    "seat_region": r.seat_region,
                    "page_number": r.page_number,
                    "source_id": r.source_id,
                })

            logger.info(
                f"Rank filter ({student_rank}, {category}, {branch}) returned {len(results)} matches."
            )
            return results
        finally:
            if should_close:
                db.close()

    def get_exact_cutoff(
        self,
        college_code: str,
        category: str,
        course_code: Optional[str] = None,
        course_name: Optional[str] = None,
        counselling_round: int = 1,
        seat_region: str = "Rest of Karnataka",
    ) -> List[Dict[str, Any]]:
        """
        Look up exact historical cutoff rank for a college and category.
        """
        db = self.get_db()
        should_close = self._db is None

        try:
            filters = [
                CutoffRecord.college_code == college_code.strip().upper(),
                CutoffRecord.category == category.strip().upper(),
                CutoffRecord.counselling_round == counselling_round,
                CutoffRecord.seat_region == seat_region,
            ]

            if course_code:
                filters.append(CutoffRecord.course_code == course_code.strip().upper())
            elif course_name:
                filters.append(CutoffRecord.course_name.ilike(f"%{course_name.strip()}%"))

            records = db.query(CutoffRecord).filter(and_(*filters)).all()
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
        finally:
            if should_close:
                db.close()

    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Return dataset distribution and summary statistics."""
        db = self.get_db()
        should_close = self._db is None

        try:
            total_records = db.query(CutoffRecord).count()
            non_null_records = (
                db.query(CutoffRecord)
                .filter(CutoffRecord.closing_rank.isnot(None))
                .count()
            )
            colleges_count = db.query(CutoffRecord.college_code).distinct().count()

            # Categories list
            categories = [
                c[0] for c in db.query(CutoffRecord.category).distinct().order_by(CutoffRecord.category).all()
            ]

            # Courses list
            courses = [
                {"code": c[0], "name": c[1]}
                for c in db.query(CutoffRecord.course_code, CutoffRecord.course_name)
                .distinct()
                .order_by(CutoffRecord.course_code)
                .all()
            ]

            # Rounds list
            rounds = [
                r[0] for r in db.query(CutoffRecord.counselling_round).distinct().all()
            ]

            # Seat regions list
            regions = [
                reg[0] for reg in db.query(CutoffRecord.seat_region).distinct().all()
            ]

            return {
                "dataset_year": settings.DATASET_YEAR,
                "total_cutoff_combinations": total_records,
                "non_null_cutoffs": non_null_records,
                "college_count": colleges_count,
                "available_categories": categories,
                "available_branches": courses,
                "available_rounds": rounds,
                "available_seat_regions": regions,
            }
        finally:
            if should_close:
                db.close()
