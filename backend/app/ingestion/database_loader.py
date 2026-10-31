import json
import logging
import os
from typing import Dict, List, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.database.connection import SessionLocal
from app.database.models import Source, CutoffRecord

logger = logging.getLogger(__name__)


def save_processed_records_to_json(
    records: List[Dict[str, Any]],
    output_path: str = "data/processed/kcet_records.json",
):
    """Save cleaned extracted records to JSON for backup and inspection."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(records)} records to {output_path}")


def load_records_into_database(
    extraction_result: Dict[str, Any],
    db: Session = None,
    batch_size: int = 2000,
) -> Dict[str, Any]:
    """
    Persist source and cutoff records into Neon PostgreSQL database.
    Prevents duplicates on repeated ingestion.
    """
    should_close_db = False
    if db is None:
        if SessionLocal is None:
            raise RuntimeError("Database connection not configured.")
        db = SessionLocal()
        should_close_db = True

    try:
        filename = extraction_result["filename"]
        year = extraction_result["year"]
        round_no = extraction_result["counselling_round"]
        region = extraction_result["seat_region"]
        raw_records = extraction_result["records"]

        # 1. Upsert Source record
        source = (
            db.query(Source)
            .filter_by(
                filename=filename,
                year=year,
                counselling_round=round_no,
                seat_region=region,
            )
            .first()
        )

        if not source:
            source = Source(
                filename=filename,
                year=year,
                counselling_round=round_no,
                seat_region=region,
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            logger.info(f"Created new source entry id={source.id} for {filename}")
        else:
            logger.info(f"Found existing source entry id={source.id} for {filename}")

        source_id = source.id

        # 2. Prepare records for batch insertion with deduplication
        # Deduplicate to prevent intra-batch cardinality violation
        unique_records_dict = {}
        for r in raw_records:
            key = (r["college_code"], r["course_name"], r["category"], year, round_no, region)
            unique_records_dict[key] = r

        unique_records = list(unique_records_dict.values())
        total_records = len(unique_records)
        inserted_count = 0

        logger.info(f"Preparing to insert {total_records} deduplicated records into cutoff_records...")

        for i in range(0, total_records, batch_size):
            batch = unique_records[i : i + batch_size]
            stmt_values = []
            for r in batch:
                stmt_values.append({
                    "college_code": r["college_code"],
                    "college_name": r["college_name"],
                    "location": r.get("location"),
                    "course_code": r["course_code"],
                    "course_name": r["course_name"],
                    "category": r["category"],
                    "closing_rank": r["closing_rank"],
                    "year": year,
                    "counselling_round": round_no,
                    "seat_region": region,
                    "source_id": source_id,
                    "page_number": r["page_number"],
                })

            stmt = insert(CutoffRecord).values(stmt_values)
            upsert_stmt = stmt.on_conflict_do_update(
                constraint="uq_cutoff_unique_combination",
                set_={
                    "closing_rank": stmt.excluded.closing_rank,
                    "page_number": stmt.excluded.page_number,
                    "college_name": stmt.excluded.college_name,
                    "location": stmt.excluded.location,
                    "course_code": stmt.excluded.course_code,
                },
            )

            db.execute(upsert_stmt)
            db.commit()
            inserted_count += len(batch)
            logger.info(f"Ingested batch: {inserted_count}/{total_records} records.")

        # 3. Save copy in processed directory
        save_processed_records_to_json(
            unique_records,
            output_path=os.path.join(
                os.path.dirname(__file__), "../../data/processed/kcet_records.json"
            ),
        )

        return {
            "source_id": source_id,
            "filename": filename,
            "total_records_processed": total_records,
            "inserted_or_updated": inserted_count,
            "colleges": extraction_result["college_count"],
            "courses": extraction_result["course_count"],
        }
    finally:
        if should_close_db:
            db.close()
