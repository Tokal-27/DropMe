"""
Metrics collection and tracking for the waste classification model
Tracks: prediction accuracy, latency, throughput, and failure rates
"""

import time
from typing import Dict, List
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and aggregates prediction metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.failed_predictions = deque(maxlen=window_size)
        self.start_time = datetime.now()
    
    def record_prediction(self, prediction_id: str, predicted_class: str, 
                         confidence: float, inference_time_ms: int, status: str = "success"):
        """Record a prediction"""
        self.predictions.append({
            "prediction_id": prediction_id,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "inference_time_ms": inference_time_ms,
            "status": status,
            "timestamp": datetime.now()
        })
        logger.info(f"Recorded prediction: {predicted_class} (confidence: {confidence:.2f}, latency: {inference_time_ms}ms)")
    
    def record_failed_prediction(self, prediction_id: str, error: str):
        """Record a failed prediction"""
        self.failed_predictions.append({
            "prediction_id": prediction_id,
            "error": error,
            "timestamp": datetime.now()
        })
        logger.warning(f"Failed prediction: {prediction_id} - {error}")
    
    def get_metrics(self) -> Dict:
        """Get aggregate metrics"""
        if not self.predictions:
            return {
                "total_predictions": 0,
                "average_confidence": 0.0,
                "latency_stats": {"min": 0, "max": 0, "avg": 0},
                "failed_predictions": len(self.failed_predictions)
            }
        
        confidences = [p["confidence"] for p in self.predictions]
        latencies = [p["inference_time_ms"] for p in self.predictions]
        
        return {
            "total_predictions": len(self.predictions),
            "average_confidence": sum(confidences) / len(confidences),
            "latency_stats": {
                "min": min(latencies),
                "max": max(latencies),
                "avg": sum(latencies) / len(latencies)
            },
            "failed_predictions": len(self.failed_predictions),
            "success_rate": (len(self.predictions) - len(self.failed_predictions)) / len(self.predictions)
        }
    
    def get_detailed_metrics(self) -> Dict:
        """Get detailed metrics for dashboard"""
        if not self.predictions:
            return {
                "class_distribution": {},
                "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
                "hourly_throughput": {}
            }
        
        # Class distribution
        class_dist = {}
        for p in self.predictions:
            cls = p["predicted_class"]
            class_dist[cls] = class_dist.get(cls, 0) + 1
        
        # Confidence distribution
        conf_dist = {"high": 0, "medium": 0, "low": 0}
        for p in self.predictions:
            conf = p["confidence"]
            if conf >= 0.85:
                conf_dist["high"] += 1
            elif conf >= 0.7:
                conf_dist["medium"] += 1
            else:
                conf_dist["low"] += 1
        
        # Hourly throughput
        now = datetime.now()
        hourly = {}
        for hour in range(24):
            hour_start = now - timedelta(hours=hour)
            count = sum(1 for p in self.predictions 
                       if hour_start <= p["timestamp"] < hour_start + timedelta(hours=1))
            hourly[f"{hour}h_ago"] = count
        
        return {
            "class_distribution": class_dist,
            "confidence_distribution": conf_dist,
            "hourly_throughput": hourly,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }
    
    def get_class_metrics(self, predicted_class: str) -> Dict:
        """Get metrics for a specific class"""
        class_preds = [p for p in self.predictions if p["predicted_class"] == predicted_class]
        
        if not class_preds:
            return {"count": 0}
        
        confidences = [p["confidence"] for p in class_preds]
        latencies = [p["inference_time_ms"] for p in class_preds]
        
        return {
            "count": len(class_preds),
            "average_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "average_latency_ms": sum(latencies) / len(latencies),
            "percentage": len(class_preds) / len(self.predictions)
        }
