"""
Configuration for the API
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_VERSION = "1.0.0"
MODEL_VERSION = "1.0.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("API_PORT", 8000))
API_WORKERS = int(os.getenv("API_WORKERS", 4))

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "./model")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.7))

# Monitoring
MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
DRIFT_DETECTION_ENABLED = os.getenv("DRIFT_DETECTION_ENABLED", "true").lower() == "true"

# Thresholds
DRIFT_ALERT_THRESHOLD = float(os.getenv("DRIFT_ALERT_THRESHOLD", 0.3))
FAILURE_ALERT_THRESHOLD = float(os.getenv("FAILURE_ALERT_THRESHOLD", 0.05))

# Rollback Configuration
ROLLBACK_ENABLED = os.getenv("ROLLBACK_ENABLED", "true").lower() == "true"
PREVIOUS_MODEL_VERSION = os.getenv("PREVIOUS_MODEL_VERSION", "0.9.9")
