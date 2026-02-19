"""
Waste Classification Model
Simulates a waste material classifier with inference capabilities.
Supports: plastic, metal, glass, organic, paper, electronic waste
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WasteClassifier:
    """Waste material classification model"""
    
    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        self.classes = ["plastic", "metal", "glass", "organic", "paper", "electronic"]
        self.model_accuracy = 0.95
        self.model_created_at = datetime.now().isoformat()
        logger.info(f"WasteClassifier v{model_version} initialized")
    
    def predict(self, image_path: str = None, material: str = None, 
                confidence_threshold: float = 0.7) -> Dict:
        """
        Predict waste classification
        
        Args:
            image_path: Path to waste image (for feature extraction)
            material: Material hint for prediction
            confidence_threshold: Minimum confidence threshold
        
        Returns:
            Dictionary with prediction results
        """
        
        # Simulate inference logic
        # In production: actual CNN model (ResNet50, EfficientNet, etc.)
        predicted_class, confidence = self._simulate_inference(material)
        
        # Check confidence threshold
        if confidence < confidence_threshold:
            return {
                "status": "low_confidence",
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "model_version": self.model_version,
                "inference_time_ms": np.random.randint(40, 60),
                "message": f"Confidence {confidence:.2f} below threshold {confidence_threshold}"
            }
        
        return {
            "status": "success",
            "predicted_class": predicted_class,
            "confidence": float(confidence),
            "model_version": self.model_version,
            "inference_time_ms": np.random.randint(40, 60),
            "class_probabilities": self._get_class_probabilities(predicted_class),
            "timestamp": datetime.now().isoformat()
        }
    
    def _simulate_inference(self, material: str = None) -> Tuple[str, float]:
        """Simulate model inference"""
        # Simulated probability distributions
        if material and material.lower() in self.classes:
            # If material hint provided, higher confidence for that class
            base_confidence = np.random.uniform(0.85, 0.98)
            return material.lower(), base_confidence
        else:
            # Random prediction
            predicted_class = np.random.choice(self.classes)
            confidence = np.random.uniform(0.70, 0.98)
            return predicted_class, confidence
    
    def _get_class_probabilities(self, predicted_class: str) -> Dict[str, float]:
        """Get probability distribution across all classes"""
        # Create probabilities with highest for predicted class
        probs = np.random.dirichlet(np.ones(len(self.classes)))
        # Boost predicted class
        probs[self.classes.index(predicted_class)] += 0.15
        probs = probs / probs.sum()  # Re-normalize
        
        return {
            cls: float(prob) 
            for cls, prob in zip(self.classes, probs)
        }
    
    def get_model_info(self) -> Dict:
        """Get model metadata"""
        return {
            "model_version": self.model_version,
            "model_created_at": self.model_created_at,
            "model_accuracy": self.model_accuracy,
            "supported_classes": self.classes,
            "framework": "TensorFlow/Keras (Simulated)",
            "input_shape": [224, 224, 3],
            "model_size_mb": 125.5
        }
    
    def validate_input(self, material: str) -> Tuple[bool, str]:
        """Validate input material"""
        if not material:
            return False, "Material parameter is required"
        
        if material.lower() not in self.classes:
            return False, f"Material must be one of: {', '.join(self.classes)}"
        
        return True, "Valid input"
    
    def batch_predict(self, materials: List[str]) -> List[Dict]:
        """Batch prediction for multiple materials"""
        predictions = []
        for material in materials:
            pred = self.predict(material=material)
            predictions.append(pred)
        return predictions


# Singleton instance
_classifier_instance = None

def get_classifier(model_version: str = "v1.0.0") -> WasteClassifier:
    """Get or create classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = WasteClassifier(model_version)
    return _classifier_instance
