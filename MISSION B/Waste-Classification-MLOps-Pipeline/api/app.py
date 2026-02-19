"""
FastAPI Application for Waste Classification Inference Service
Production-grade API with monitoring, versioning, and error handling
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from datetime import datetime
import uuid
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.waste_classifier import get_classifier
from config import API_VERSION, MODEL_VERSION
from monitoring.metrics import MetricsCollector
from monitoring.drift_detection import DriftDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
metrics_collector = MetricsCollector()
drift_detector = DriftDetector()


# ============ Pydantic Models ============

class PredictionRequest(BaseModel):
    """Request model for waste classification"""
    image_path: str = Field(..., description="Path to waste image")
    material: str = Field(..., description="Material hint (optional)", example="plastic")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum confidence")


class PredictionResponse(BaseModel):
    """Response model for waste classification"""
    prediction_id: str
    status: str
    predicted_class: str
    confidence: float
    model_version: str
    api_version: str
    inference_time_ms: int
    timestamp: str
    class_probabilities: dict = None
    message: str = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    api_version: str
    model_version: str
    timestamp: str


class MetricsResponse(BaseModel):
    """Metrics response"""
    total_predictions: int
    average_confidence: float
    prediction_latency_ms: dict
    model_drift_score: float
    failed_predictions: int
    timestamp: str


# ============ Lifespan Management ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    logger.info(f"Starting Waste Classification API v{API_VERSION}")
    logger.info(f"Model Version: {MODEL_VERSION}")
    classifier = get_classifier(MODEL_VERSION)
    logger.info(f"Model info: {classifier.get_model_info()}")
    yield
    logger.info("Shutting down API")


# ============ Application ============

app = FastAPI(
    title="Waste Classification MLOps Pipeline",
    description="Production inference service for waste material classification",
    version=API_VERSION,
    lifespan=lifespan
)


# ============ Root & Health Endpoints ============

@app.get("/", tags=["info"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Waste Classification MLOps Pipeline",
        "version": API_VERSION,
        "model_version": MODEL_VERSION,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "metrics": "/metrics",
            "model_info": "/model-info"
        }
    }


@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        api_version=API_VERSION,
        model_version=MODEL_VERSION,
        timestamp=datetime.now().isoformat()
    )


# ============ Prediction Endpoints ============

@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
async def predict(request: PredictionRequest, background_tasks: BackgroundTasks):
    """
    Classify waste material from image or prediction data
    
    Returns classification result with confidence and metadata
    """
    prediction_id = str(uuid.uuid4())
    
    try:
        # Validate input
        classifier = get_classifier()
        is_valid, message = classifier.validate_input(request.material)
        
        if not is_valid:
            logger.warning(f"Invalid input for prediction {prediction_id}: {message}")
            raise HTTPException(status_code=400, detail=message)
        
        # Get prediction
        logger.info(f"Processing prediction {prediction_id} for material: {request.material}")
        result = classifier.predict(
            image_path=request.image_path,
            material=request.material,
            confidence_threshold=request.confidence_threshold
        )
        
        # Prepare response
        response = PredictionResponse(
            prediction_id=prediction_id,
            status=result.get("status", "success"),
            predicted_class=result["predicted_class"],
            confidence=result["confidence"],
            model_version=result["model_version"],
            api_version=API_VERSION,
            inference_time_ms=result["inference_time_ms"],
            timestamp=datetime.now().isoformat(),
            class_probabilities=result.get("class_probabilities"),
            message=result.get("message")
        )
        
        # Track metrics asynchronously
        background_tasks.add_task(
            metrics_collector.record_prediction,
            prediction_id=prediction_id,
            predicted_class=response.predicted_class,
            confidence=response.confidence,
            inference_time_ms=response.inference_time_ms,
            status=response.status
        )
        
        logger.info(f"Prediction {prediction_id} completed: {response.predicted_class} ({response.confidence:.2f})")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing prediction {prediction_id}: {str(e)}")
        metrics_collector.record_failed_prediction(prediction_id, str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", tags=["prediction"])
async def predict_batch(materials: list[str], background_tasks: BackgroundTasks):
    """Batch prediction for multiple materials"""
    classifier = get_classifier()
    results = []
    
    for material in materials:
        pred = classifier.predict(material=material)
        pred["prediction_id"] = str(uuid.uuid4())
        results.append(pred)
        
        background_tasks.add_task(
            metrics_collector.record_prediction,
            prediction_id=pred["prediction_id"],
            predicted_class=pred["predicted_class"],
            confidence=pred["confidence"],
            inference_time_ms=pred["inference_time_ms"],
            status=pred.get("status", "success")
        )
    
    return {
        "total_predictions": len(results),
        "predictions": results,
        "timestamp": datetime.now().isoformat()
    }


# ============ Model Info ============

@app.get("/model-info", tags=["info"])
async def model_info():
    """Get model metadata and performance metrics"""
    classifier = get_classifier()
    return classifier.get_model_info()


# ============ Metrics & Monitoring ============

@app.get("/metrics", response_model=MetricsResponse, tags=["monitoring"])
async def get_metrics():
    """Get current performance metrics and model drift score"""
    metrics = metrics_collector.get_metrics()
    drift_score = drift_detector.get_drift_score()
    
    return MetricsResponse(
        total_predictions=metrics["total_predictions"],
        average_confidence=metrics["average_confidence"],
        prediction_latency_ms=metrics["latency_stats"],
        model_drift_score=drift_score,
        failed_predictions=metrics["failed_predictions"],
        timestamp=datetime.now().isoformat()
    )


@app.get("/metrics/detailed", tags=["monitoring"])
async def get_detailed_metrics():
    """Get detailed metrics for dashboard"""
    metrics = metrics_collector.get_detailed_metrics()
    drift_info = drift_detector.get_drift_details()
    
    return {
        "metrics": metrics,
        "drift_detection": drift_info,
        "timestamp": datetime.now().isoformat()
    }


# ============ Error Handlers ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
