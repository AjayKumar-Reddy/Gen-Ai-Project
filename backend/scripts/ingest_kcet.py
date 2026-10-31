import argparse
import logging
import sys
import os
import time

from app.config.settings import get_settings
from app.database.schema import init_db
from app.ingestion.pdf_extractor import extract_cutoff_pdf
from app.ingestion.database_loader import load_records_into_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ingest_kcet")


def main():
    parser = argparse.ArgumentParser(description="Ingest official KCET cutoff PDF into Neon PostgreSQL.")
    parser.add_argument(
        "--file",
        type=str,
        default="data/raw/kcet_cutoff.pdf",
        help="Path to the KCET cutoff PDF file.",
    )
    parser.add_argument("--year", type=int, default=2026, help="Counselling year (default: 2026)")
    parser.add_argument("--round", type=int, default=1, help="Counselling round (default: 1)")
    parser.add_argument(
        "--region",
        type=str,
        default="Rest of Karnataka",
        help="Seat region (default: 'Rest of Karnataka')",
    )

    args = parser.parse_args()
    settings = get_settings()

    logger.info("=" * 65)
    logger.info("KCET PDF INGESTION PIPELINE")
    logger.info("=" * 65)
    logger.info(f"Target PDF File: {args.file}")
    logger.info(f"Year: {args.year} | Round: {args.round} | Region: {args.region}")

    start_time = time.time()

    # Step 1: Ensure database schema and pgvector are initialized
    logger.info("Step 1: Checking and initializing Neon database tables...")
    init_db()

    # Step 2: Extract structured records from PDF
    logger.info("Step 2: Extracting college and cutoff tables from PDF with PyMuPDF...")
    extraction_result = extract_cutoff_pdf(
        pdf_path=args.file,
        year=args.year,
        counselling_round=args.round,
        seat_region=args.region,
    )

    logger.info(f"  Colleges Found: {extraction_result['college_count']}")
    logger.info(f"  Courses Found: {extraction_result['course_count']}")
    logger.info(f"  Total Cutoff Combinations: {len(extraction_result['records'])}")
    non_null_count = sum(1 for r in extraction_result["records"] if r["closing_rank"] is not None)
    logger.info(f"  Non-Null Cutoff Values: {non_null_count}")

    # Step 3: Load into Neon database
    logger.info("Step 3: Persisting records into Neon PostgreSQL...")
    load_result = load_records_into_database(extraction_result)

    elapsed = time.time() - start_time
    logger.info("=" * 65)
    logger.info("INGESTION COMPLETED SUCCESSFULLY")
    logger.info("=" * 65)
    logger.info(f"Source ID: {load_result['source_id']}")
    logger.info(f"Records Ingested/Updated: {load_result['inserted_or_updated']}")
    logger.info(f"Elapsed Time: {elapsed:.2f} seconds")
    logger.info("=" * 65)


if __name__ == "__main__":
    main()

