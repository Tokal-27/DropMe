"""
Tests for monitoring and drift detection
"""

import pytest
from monitoring.drift_detection import DriftDetector
from monitoring.metrics import MetricsCollector


@pytest.fixture
def drift_detector():
    return DriftDetector()


@pytest.fixture
def metrics_collector():
    return MetricsCollector()


def test_drift_detector_initialization(drift_detector):
    assert drift_detector.get_drift_score() == 0.0


def test_drift_detector_update(drift_detector):
    # Add some predictions
    for _ in range(50):
        drift_detector.update("plastic", 0.95)
    
    score = drift_detector.get_drift_score()
    assert 0 <= score <= 1


def test_metrics_collection(metrics_collector):
    # Record predictions
    metrics_collector.record_prediction("pred_1", "plastic", 0.95, 50)
    metrics_collector.record_prediction("pred_2", "metal", 0.92, 48)
    
    metrics = metrics_collector.get_metrics()
    assert metrics["total_predictions"] == 2
    assert metrics["average_confidence"] > 0.9


def test_failed_prediction_tracking(metrics_collector):
    metrics_collector.record_failed_prediction("pred_fail", "test error")
    metrics = metrics_collector.get_metrics()
    assert metrics["failed_predictions"] == 1
