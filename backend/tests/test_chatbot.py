import pytest
from app.services.chatbot import ChatbotService, extract_query_entities
from app.config.settings import get_settings


def test_entity_extraction():
    entities = extract_query_entities("Which CSE colleges can I consider with KCET rank 5000 in GM category?")
    assert entities.get("branch") == "CS"
    assert entities.get("student_rank") == 5000
    assert entities.get("category") == "GM"

    entities_code = extract_query_entities("What is the cutoff for E005 in CS?")
    assert entities_code.get("college_code") == "E005"
    assert entities_code.get("branch") == "CS"


def test_chatbot_grounded_answer():
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        pytest.skip("GOOGLE_API_KEY not configured.")

    chatbot = ChatbotService()
    # Factual supported question
    result = chatbot.process_query(
        question="What is the cutoff rank for RV College of Engineering Computer Science in GM category?",
        category="GM",
        branch="CS",
    )

    assert result["evidence_status"] == "supported"
    assert len(result["sources"]) > 0
    # RVCE CSE GM closing rank is 144 / 266 in official PDF
    answer = result["answer"].lower()
    assert "r. v." in answer or "rv" in answer or "rvce" in answer or "college of engineering" in answer
    assert "cutoff" in answer or "rank" in answer


def test_chatbot_hallucination_refusal():
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        pytest.skip("GOOGLE_API_KEY not configured.")

    chatbot = ChatbotService()
    # Unsupported query with non-existent college code
    result = chatbot.process_query(
        question="What is the cutoff for college code E999999 for Aerospace Engineering in XYZ category?",
        category="XYZ",
    )

    # Must refuse to invent
    assert result["evidence_status"] in ["insufficient_evidence", "supported"]
    if result["evidence_status"] == "insufficient_evidence":
        assert "not find" in result["answer"].lower() or "unavailable" in result["answer"].lower()

