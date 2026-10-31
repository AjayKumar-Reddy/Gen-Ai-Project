import os
import pytest
from app.ingestion.data_cleaner import (
    clean_rank_value,
    extract_location,
    map_course_to_code,
)
from app.ingestion.pdf_extractor import extract_cutoff_pdf

PDF_PATH = os.path.join(os.path.dirname(__file__), "../data/raw/kcet_cutoff.pdf")


def test_clean_rank_value():
    # Valid integers
    assert clean_rank_value("144") == 144
    assert clean_rank_value("425") == 425
    # Decimal rank (tie breaker)
    assert clean_rank_value("4015.5") == 4016
    # Missing values preserved as None, NEVER 0
    assert clean_rank_value("--") is None
    assert clean_rank_value("-") is None
    assert clean_rank_value("") is None
    assert clean_rank_value("0") is None
    assert clean_rank_value(None) is None


def test_location_extraction():
    name, loc = extract_location("R. V. College of Engineering, Bangalore(AUTONOMOUS) MYSORE ROAD,BANGALORE")
    assert loc == "Bangalore"
    assert "College of Engineering" in name

    name, loc = extract_location("Malnad College of Engineering, Hassan(AUTONOMOUS) SALAGAME ROAD,HASSSAN")
    assert loc == "Hassan"


def test_course_code_mapping():
    code, std_name = map_course_to_code("COMPUTER SCIENCE AND ENGINEERING")
    assert code == "CS"
    assert "Computer Science" in std_name

    code, std_name = map_course_to_code("ELECTRONICS AND COMMUNICATION ENGG")
    assert code == "EC"

    code, std_name = map_course_to_code("MECHANICAL ENGINEERING")
    assert code == "ME"

    code, std_name = map_course_to_code("CIVIL ENGINEERING")
    assert code == "CV"


@pytest.mark.skipif(not os.path.exists(PDF_PATH), reason="PDF file not found")
def test_pdf_extraction_sample():
    # Run extractor on actual official PDF
    result = extract_cutoff_pdf(PDF_PATH, year=2026, counselling_round=1)

    assert result["total_pages"] == 69
    assert result["college_count"] >= 200
    assert result["course_count"] >= 1500
    assert len(result["records"]) > 50000

    # Test RVCE (E005) CSE GM cutoff
    rvce_cse_gm = [
        r for r in result["records"]
        if r["college_code"] == "E005"
        and r["course_code"] == "CS"
        and r["category"] == "GM"
    ]
    assert len(rvce_cse_gm) >= 1
    # On page 2 of PDF, RVCE CSE GM cutoff is 144
    assert rvce_cse_gm[0]["closing_rank"] == 144
    assert rvce_cse_gm[0]["page_number"] == 2

    # Verify no rank is 0
    zero_ranks = [r for r in result["records"] if r["closing_rank"] == 0]
    assert len(zero_ranks) == 0

    # Verify missing ranks are None
    missing_ranks = [r for r in result["records"] if r["closing_rank"] is None]
    assert len(missing_ranks) > 0

