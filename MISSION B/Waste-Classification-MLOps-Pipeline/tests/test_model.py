"""
Unit tests for waste classifier model
"""

import pytest
from model.waste_classifier import WasteClassifier, get_classifier


@pytest.fixture
def classifier():
    return WasteClassifier(model_version="v1.0.0")


def test_classifier_initialization(classifier):
    assert classifier.model_version == "v1.0.0"
    assert len(classifier.classes) == 6
    assert classifier.model_accuracy == 0.95


def test_predict_with_material(classifier):
    result = classifier.predict(material="plastic")
    assert result["status"] == "success"
    assert result["predicted_class"] == "plastic"
    assert 0 <= result["confidence"] <= 1


def test_predict_invalid_material(classifier):
    is_valid, message = classifier.validate_input("invalid_material")
    assert not is_valid
    assert "Material must be one of" in message


def test_confidence_threshold(classifier):
    # With high threshold, might get low_confidence status
    result = classifier.predict(material="plastic", confidence_threshold=0.99)
    assert result["status"] in ["success", "low_confidence"]


def test_batch_predict(classifier):
    materials = ["plastic", "metal", "glass"]
    results = classifier.batch_predict(materials)
    assert len(results) == 3
    assert all(r["status"] in ["success", "low_confidence"] for r in results)


def test_model_info(classifier):
    info = classifier.get_model_info()
    assert info["model_version"] == "v1.0.0"
    assert info["model_accuracy"] == 0.95
    assert "plastic" in info["supported_classes"]


def test_singleton_pattern():
    c1 = get_classifier()
    c2 = get_classifier()
    assert c1 is c2
