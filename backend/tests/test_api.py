import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import get_settings

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cutoff_combinations"] > 0
    assert data["college_count"] > 200
    assert "GM" in data["available_categories"]


def test_cutoffs_endpoint():
    response = client.get("/api/cutoffs?college_code=E005&category=GM&course_code=CS")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["college_code"] == "E005"
    assert data[0]["closing_rank"] is not None


def test_colleges_filter_endpoint():
    response = client.get("/api/colleges?branch=CS&category=GM&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    for item in data:
        assert item["course_code"] == "CS"
        assert item["category"] == "GM"


def test_chat_endpoint_rank_query():
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        pytest.skip("GOOGLE_API_KEY not configured.")

    payload = {
        "question": "Which CSE colleges can I consider with rank 5000 in GM category?",
        "student_rank": 5000,
        "category": "GM",
        "branch": "CS",
        "round": 1,
        "seat_region": "Rest of Karnataka",
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["evidence_status"] == "supported"
    assert len(data["results"]) > 0
    assert len(data["sources"]) > 0
    assert "colleges" in data


def test_chat_endpoint_alias_payload():
    """Verify that frontend payload using 'query', 'rank', 'region' aliases parses correctly."""
    settings = get_settings()
    if not settings.GOOGLE_API_KEY:
        pytest.skip("GOOGLE_API_KEY not configured.")

    payload = {
        "query": "Can I get BMS College of Engineering in CS with rank 3500 (GM)?",
        "rank": 3000,
        "category": "GM",
        "round": 1,
        "region": "General",
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "colleges" in data
    assert "sources" in data
