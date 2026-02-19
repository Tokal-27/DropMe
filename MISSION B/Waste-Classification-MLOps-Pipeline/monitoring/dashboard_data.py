"""
Dashboard data aggregation for AI Waste Intelligence Dashboard
Prepares metrics for visualization and reporting
"""

from typing import Dict, List
from datetime import datetime
import json


class DashboardDataAggregator:
    """Aggregates data for dashboard visualization"""
    
    def __init__(self, metrics_collector, drift_detector):
        self.metrics_collector = metrics_collector
        self.drift_detector = drift_detector
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        metrics = self.metrics_collector.get_detailed_metrics()
        drift = self.drift_detector.get_drift_details()
        
        return {
            "summary": {
                "total_predictions": self.metrics_collector.get_metrics()["total_predictions"],
                "success_rate": self.metrics_collector.get_metrics().get("success_rate", 0),
                "average_latency_ms": self.metrics_collector.get_metrics()["latency_stats"]["avg"],
                "model_drift_score": drift["drift_score"],
                "drift_status": drift["drift_status"]
            },
            "metrics": metrics,
            "drift_details": drift,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_metrics_json(self, filepath: str):
        """Export metrics to JSON file"""
        dashboard_data = self.get_dashboard_data()
        with open(filepath, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
