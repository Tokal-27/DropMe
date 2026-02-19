"""
Model drift detection using statistical methods
Detects distribution shifts in model predictions and inputs
"""

import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detects model drift and concept drift"""
    
    WASTE_CLASSES = ["plastic", "metal", "glass", "organic", "paper", "electronic"]
    
    def __init__(self, reference_window: int = 100, test_window: int = 100):
        self.reference_window = reference_window
        self.test_window = test_window
        self.reference_distribution = deque(maxlen=reference_window)
        self.recent_distribution = deque(maxlen=test_window)
        self.confidence_history = deque(maxlen=test_window)
        self.predictions_history = deque(maxlen=test_window * 10)
        self.drift_alerts = []
        
        # Initialize reference distribution (expected from training)
        self.expected_distribution = {
            "plastic": 0.18,
            "metal": 0.16,
            "glass": 0.17,
            "organic": 0.16,
            "paper": 0.18,
            "electronic": 0.15
        }
    
    def update(self, predicted_class: str, confidence: float, 
               class_probabilities: Dict[str, float] = None):
        """Update drift detector with new prediction"""
        self.recent_distribution.append(predicted_class)
        self.confidence_history.append(confidence)
        
        # Record for detailed analysis
        self.predictions_history.append({
            "class": predicted_class,
            "confidence": confidence,
            "probabilities": class_probabilities or {},
            "timestamp": datetime.now()
        })
    
    def get_drift_score(self) -> float:
        """
        Calculate overall model drift score (0.0 to 1.0)
        0.0 = no drift, 1.0 = maximum drift
        """
        if len(self.recent_distribution) < self.test_window // 2:
            return 0.0
        
        # Chi-squared test for distribution shift
        chi_squared = self._chi_squared_drift()
        
        # Confidence degradation
        confidence_drift = self._confidence_drift()
        
        # Combine scores
        total_score = (chi_squared * 0.6 + confidence_drift * 0.4)
        
        return min(total_score, 1.0)
    
    def _chi_squared_drift(self) -> float:
        """Perform chi-squared test for drift"""
        if len(self.recent_distribution) == 0:
            return 0.0
        
        # Observed distribution
        observed = self._get_class_distribution(self.recent_distribution)
        
        # Expected distribution
        expected = self.expected_distribution
        
        # Chi-squared calculation
        chi_squared = 0.0
        for cls in self.WASTE_CLASSES:
            obs = observed.get(cls, 0) * len(self.recent_distribution)
            exp = expected.get(cls, 0) * len(self.recent_distribution)
            
            if exp > 0:
                chi_squared += ((obs - exp) ** 2) / exp
        
        # Normalize to [0, 1] scale
        # df = 5 (6 classes - 1)
        normalized_score = min(chi_squared / 10.0, 1.0)
        
        return normalized_score
    
    def _confidence_drift(self) -> float:
        """Detect confidence degradation"""
        if len(self.confidence_history) < 10:
            return 0.0
        
        recent_conf = list(self.confidence_history)[-50:] if len(self.confidence_history) >= 50 else list(self.confidence_history)
        
        avg_confidence = np.mean(recent_conf)
        conf_std = np.std(recent_conf)
        
        # Expected average confidence should be ~0.90
        expected_confidence = 0.90
        
        # Score based on deviation from expected
        confidence_score = abs(avg_confidence - expected_confidence) / expected_confidence
        confidence_score = min(confidence_score, 1.0)
        
        return confidence_score
    
    def _get_class_distribution(self, data) -> Dict[str, float]:
        """Get class distribution from deque"""
        total = len(data)
        if total == 0:
            return {cls: 0.0 for cls in self.WASTE_CLASSES}
        
        dist = {}
        for cls in self.WASTE_CLASSES:
            count = sum(1 for x in data if x == cls)
            dist[cls] = count / total
        
        return dist
    
    def get_drift_details(self) -> Dict:
        """Get detailed drift information"""
        drift_score = self.get_drift_score()
        
        observed_dist = self._get_class_distribution(self.recent_distribution)
        
        return {
            "drift_score": float(drift_score),
            "drift_status": self._get_drift_status(drift_score),
            "observed_distribution": observed_dist,
            "expected_distribution": self.expected_distribution,
            "average_confidence": float(np.mean(self.confidence_history)) if self.confidence_history else 0.0,
            "confidence_std": float(np.std(self.confidence_history)) if len(self.confidence_history) > 1 else 0.0,
            "predictions_analyzed": len(self.recent_distribution),
            "alerts": self.drift_alerts[-10:] if self.drift_alerts else []
        }
    
    def _get_drift_status(self, score: float) -> str:
        """Get human-readable drift status"""
        if score < 0.1:
            return "No Drift"
        elif score < 0.3:
            return "Minor Drift"
        elif score < 0.6:
            return "Moderate Drift"
        else:
            return "Severe Drift"
    
    def check_anomaly(self, predicted_class: str, confidence: float) -> Tuple[bool, str]:
        """
        Check if a prediction is anomalous
        Returns: (is_anomaly, reason)
        """
        
        # Low confidence anomaly
        if confidence < 0.6:
            return True, f"Low confidence prediction: {confidence:.2f}"
        
        # Unusual class prediction
        if len(self.recent_distribution) > 20:
            dist = self._get_class_distribution(self.recent_distribution)
            class_freq = dist.get(predicted_class, 0)
            
            if class_freq < 0.05:  # Rare class in recent predictions
                return True, f"Rare class prediction: {predicted_class}"
        
        return False, ""
