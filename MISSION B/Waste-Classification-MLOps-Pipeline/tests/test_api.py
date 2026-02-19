"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_predict_endpoint(client):
    payload = {
        "image_path": "test.jpg",
        "material": "plastic",
        "confidence_threshold": 0.7
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_class" in data
    assert "confidence" in data
    assert "prediction_id" in data


def test_predict_invalid_material(client):
    payload = {
        "image_path": "test.jpg",
        "material": "invalid_material",
        "confidence_threshold": 0.7
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 400


def test_metrics_endpoint(client):
    # Make some predictions first
    payload = {"image_path": "test.jpg", "material": "plastic", "confidence_threshold": 0.7}
    client.post("/predict", json=payload)
    
    # Then check metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "model_drift_score" in data


def test_model_info_endpoint(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "supported_classes" in data
