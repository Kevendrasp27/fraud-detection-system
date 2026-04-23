import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)

VALID_TRANSACTION = {
    "amount": 5000.0,
    "oldbalanceOrg": 20000.0,
    "newbalanceOrig": 15000.0,
    "oldbalanceDest": 1000.0,
    "newbalanceDest": 6000.0
}

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

def test_predict_returns_valid_structure():
    response = client.post("/predict", json=VALID_TRANSACTION)
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert data["prediction"] in ["Fraud", "Safe"]
        assert 0.0 <= data["probability"] <= 1.0

def test_predict_rejects_negative_amount():
    bad = {**VALID_TRANSACTION, "amount": -100}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_predict_rejects_missing_fields():
    response = client.post("/predict", json={"amount": 1000})
    assert response.status_code == 422

def test_predict_rejects_zero_amount():
    bad = {**VALID_TRANSACTION, "amount": 0}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200
