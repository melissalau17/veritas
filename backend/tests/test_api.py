"""
API integration tests for FastAPI endpoints.
"""

import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """GET /api/health returns status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Veritas"


def test_create_investigation_endpoint():
    """POST /api/investigations creates a valid investigation."""
    payload = {
        "problem": "Pump P-101 has abnormal vibration after its coupling was replaced. What should the engineer investigate?"
    }
    response = client.post("/api/investigations", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "investigation_id" in data
    assert data["status"] == "completed"
    assert "result" in data

    result = data["result"]
    assert result["incident"]["asset_id"] == "P-101"
    assert len(result["revision_checks"]) > 0
    assert len(result["conflicts"]) > 0
    assert len(result["relevant_evidence"]) > 0
    assert len(result["hypotheses"]) > 0
    assert len(result["trace"]) > 0

    # Test retrieval endpoint
    inv_id = data["investigation_id"]
    get_res = client.get(f"/api/investigations/{inv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["investigation_id"] == inv_id


def test_create_investigation_validation_error():
    """POST /api/investigations with empty problem returns 400."""
    response = client.post("/api/investigations", json={"problem": "   "})
    assert response.status_code == 400

