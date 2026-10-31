import pytest
from app.embeddings.embedding_service import format_cutoff_document, extract_record_metadata, EmbeddingService
from app.config.settings import get_settings


class MockRecord:
    def __init__(self):
        self.id = 101
        self.college_code = "E005"
        self.college_name = "RV College of Engineering"
        self.location = "Bangalore"
        self.course_code = "CS"
        self.course_name = "Computer Science and Engineering"
        self.category = "GM"
        self.closing_rank = 425
        self.year = 2026
        self.counselling_round = 1
        self.seat_region = "Rest of Karnataka"
        self.source_id = 1
        self.page_number = 2


def test_format_cutoff_document():
    rec = MockRecord()
    doc_text = format_cutoff_document(rec)
    assert "College Code: E005" in doc_text
    assert "RV College of Engineering" in doc_text
    assert "Course Code: CS" in doc_text
    assert "Category: GM" in doc_text
    assert "Closing Rank: 425" in doc_text
    assert "Page: 2" in doc_text


def test_extract_record_metadata():
    rec = MockRecord()
    meta = extract_record_metadata(rec)
    assert meta["cutoff_record_id"] == 101
    assert meta["college_code"] == "E005"
    assert meta["closing_rank"] == 425
    assert meta["category"] == "GM"
    assert meta["page_number"] == 2


def test_embedding_service_initialization():
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        pytest.skip("GOOGLE_API_KEY not configured.")
    service = EmbeddingService()
    assert service.dimension == 768
    assert "gemini-embedding-001" in service.model

    # Generate single test query embedding
    vec = service.embed_query("RV College CSE cutoff")
    assert len(vec) == 768
    assert all(isinstance(v, float) for v in vec)

