import argparse
import logging
import sys
import time

from app.database.schema import init_db
from app.embeddings.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rebuild_indexes")


def main():
    parser = argparse.ArgumentParser(description="Generate and populate Gemini embeddings in pgvector.")
    parser.add_argument("--batch-size", type=int, default=50, help="Embedding batch size (default: 50)")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for number of documents to embed")
    parser.add_argument(
        "--all-records",
        action="store_true",
        help="Embed all records including missing values (default is only records with valid closing ranks)",
    )

    args = parser.parse_args()

    logger.info("=" * 65)
    logger.info("GEMINI EMBEDDING & PGVECTOR INDEXATION PIPELINE")
    logger.info("=" * 65)
    logger.info(f"Batch Size: {args.batch_size} | Limit: {args.limit}")

    start_time = time.time()
    service = EmbeddingService()

    logger.info(f"Model: {service.model} | Dimension: {service.dimension}")
    result = service.sync_cutoff_documents(
        batch_size=args.batch_size,
        limit=args.limit,
        only_non_null=not args.all_records,
    )

    elapsed = time.time() - start_time
    logger.info("=" * 65)
    logger.info(f"Indexing completed in {elapsed:.2f} seconds.")
    logger.info(f"Result: {result}")
    logger.info("=" * 65)


if __name__ == "__main__":
    main()

