import logging
import os
import re
from typing import Dict, List, Any
import pymupdf

from app.ingestion.data_cleaner import (
    clean_rank_value,
    extract_location,
    map_course_to_code,
    normalize_whitespace,
)

logger = logging.getLogger(__name__)

# All 37 official KEA category columns from the engineering cutoff PDF
CATEGORIES = [
    "1G", "1K", "1R", "2AG", "2AK", "2AR", "2BG", "2BK", "2BR",
    "3AG", "3AK", "3AR", "3BG", "3BK", "3BR", "GM", "GMK", "GMP", "GMR",
    "NRI", "OPN", "OTH", "S1G", "S1K", "S1R", "S2G", "S2K", "S2R",
    "S3G", "S3K", "S3R", "S4G", "S4K", "S4R", "STG", "STK", "STR"
]


def is_rank_token(t: str) -> bool:
    if t == "--":
        return True
    try:
        float(t)
        return True
    except ValueError:
        return False


def extract_cutoff_pdf(
    pdf_path: str,
    year: int = 2026,
    counselling_round: int = 1,
    seat_region: str = "Rest of Karnataka",
) -> Dict[str, Any]:
    """
    Extract structured KCET cutoff records from official KEA PDF across all pages.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    logger.info(f"Opening KCET cutoff PDF: {pdf_path}")
    doc = pymupdf.open(pdf_path)
    filename = os.path.basename(pdf_path)
    total_pages = len(doc)

    records: List[Dict[str, Any]] = []
    colleges_found = set()
    courses_count = 0
    errors: List[str] = []

    for pno in range(total_pages):
        page = doc[pno]
        raw_lines = [l.strip() for l in page.get_text("text").split("\n") if l.strip()]

        # Tokenize and merge split decimal digits (e.g. ['137004.7', '5'] -> '137004.75')
        tokens: List[str] = []
        for l in raw_lines:
            for t in l.split():
                if (
                    tokens
                    and re.match(r"^\d+\.\d$", tokens[-1])
                    and len(t) == 1
                    and t.isdigit()
                ):
                    tokens[-1] = tokens[-1] + t
                else:
                    tokens.append(t)

        i = 0
        curr_code = None
        curr_college_name = None
        curr_location = None

        while i < len(tokens):
            # Check footer
            if tokens[i] == "SC" and i + 1 < len(tokens) and tokens[i + 1] == "sub":
                break
            if tokens[i] == "Generated" and i + 1 < len(tokens) and tokens[i + 1] == "on:":
                break

            # Check for College Header
            if tokens[i] == "College:":
                i += 1
                if i < len(tokens):
                    curr_code = tokens[i]
                    i += 1
                    cname_parts = []
                    while (
                        i < len(tokens)
                        and tokens[i] not in ["Course", "CourseName", "College:"]
                        and tokens[i] not in CATEGORIES
                    ):
                        if tokens[i] == "SC" and i + 1 < len(tokens) and tokens[i + 1] == "sub":
                            break
                        if tokens[i] == "Generated" and i + 1 < len(tokens) and tokens[i + 1] == "on:":
                            break
                        cname_parts.append(tokens[i])
                        i += 1
                    raw_college_str = " ".join(cname_parts)
                    clean_name, loc = extract_location(raw_college_str)
                    curr_college_name = clean_name
                    curr_location = loc
                    colleges_found.add(curr_code)
                    continue

            # Skip header keywords
            if tokens[i] in ["Course", "Name", "CourseName"] or tokens[i] in CATEGORIES:
                i += 1
                continue
            if tokens[i] in [
                "Non-Interactive", "Admission", "System", "UGCET-2026",
                "PROVISIONA", "PROVISIONAL", "ALLOTMENT", "CUT-OFF", "RANKS",
                "FOR", "Engineering", "Seat", "Type:", "Rest", "Of", "karnataka",
                "Cut-Off", "Ranks", "KARNATAKA", "EXAMINATIONS", "AUTHORITY"
            ]:
                i += 1
                continue

            # Read course name tokens
            cname_tokens = []
            while (
                i < len(tokens)
                and not is_rank_token(tokens[i])
                and tokens[i] != "College:"
            ):
                if tokens[i] in CATEGORIES or tokens[i] in ["Course", "Name", "CourseName"]:
                    break
                if tokens[i] == "SC" and i + 1 < len(tokens) and tokens[i + 1] == "sub":
                    break
                if tokens[i] == "Generated" and i + 1 < len(tokens) and tokens[i + 1] == "on:":
                    break
                cname_tokens.append(tokens[i])
                i += 1

            raw_course_name = " ".join(cname_tokens).strip()
            if not raw_course_name:
                i += 1
                continue

            # Read the 37 rank values
            ranks = []
            while i < len(tokens) and is_rank_token(tokens[i]) and len(ranks) < len(CATEGORIES):
                ranks.append(tokens[i])
                i += 1

            if len(ranks) == len(CATEGORIES) and curr_code:
                courses_count += 1
                course_code, standard_course_name = map_course_to_code(raw_course_name)

                for cat, rk_str in zip(CATEGORIES, ranks):
                    closing_rank = clean_rank_value(rk_str)
                    records.append({
                        "college_code": curr_code,
                        "college_name": curr_college_name,
                        "location": curr_location,
                        "course_code": course_code,
                        "course_name": standard_course_name,
                        "category": cat,
                        "closing_rank": closing_rank,
                        "year": year,
                        "counselling_round": counselling_round,
                        "seat_region": seat_region,
                        "page_number": pno + 1,
                    })
            else:
                if len(ranks) > 0 and len(ranks) != len(CATEGORIES):
                    msg = (
                        f"Page {pno + 1}: Unexpected rank count ({len(ranks)}) for course "
                        f"'{raw_course_name}' under college {curr_code}"
                    )
                    logger.warning(msg)
                    errors.append(msg)

    logger.info(
        f"Extraction complete for '{filename}': {len(colleges_found)} colleges, "
        f"{courses_count} courses, {len(records)} total cutoff combinations."
    )

    return {
        "filename": filename,
        "year": year,
        "counselling_round": counselling_round,
        "seat_region": seat_region,
        "total_pages": total_pages,
        "records": records,
        "college_count": len(colleges_found),
        "course_count": courses_count,
        "errors": errors,
    }
