from fastapi import FastAPI, Request
from pydantic import BaseModel
import random
import time
import logging

# إعداد نظام الـ Logging عشان يطبع بصيغة تناسب الـ Dashboards (زي ELK أو CloudWatch)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WasteMLOps-Monitor")

app = FastAPI(title="Waste Classification API", version="1.1.0")

class InferenceRequest(BaseModel):
    image_url: str
    sensor_id: str

class InferenceResponse(BaseModel):
    prediction: str
    confidence_score: float
    processing_time_ms: int

WASTE_CATEGORIES = ["Plastic", "Paper", "Glass", "Metal", "Organic"]

# حد الثقة اللي لو الموديل نزل عنه، نعتبره "Failed Prediction"
CONFIDENCE_THRESHOLD = 0.75

@app.post("/predict", response_model=InferenceResponse)
async def predict_waste(request: InferenceRequest, req: Request):
    start_time = time.time()
    
    # Simulation
    time.sleep(random.uniform(0.1, 0.4))
    prediction = random.choice(WASTE_CATEGORIES)
    confidence = round(random.uniform(0.60, 0.99), 2)
    processing_time = int((time.time() - start_time) * 1000)
    
    # ---------------- MONITORING LOGIC ---------------- #
    
    # 1. Tracking Failed Predictions (تتبع التوقعات الفاشلة/الضعيفة)
    if confidence < CONFIDENCE_THRESHOLD:
        logger.warning(
            f"LOW_CONFIDENCE_ALERT | Sensor: {request.sensor_id} | "
            f"Prediction: {prediction} ({confidence}) | Image: {request.image_url}"
        )
        # في بيئة العمل الحقيقية، الصورة دي بتتبعت لـ Queue عشان إنسان يراجعها
    
    # 2. General Metrics for Dashboard (بيانات للوحة المراقبة)
    logger.info(
        f"METRIC_LOG | Endpoint: /predict | Method: POST | "
        f"Latency: {processing_time}ms | Result: {prediction} | Score: {confidence}"
    )
    
    return InferenceResponse(
        prediction=prediction,
        confidence_score=confidence,
        processing_time_ms=processing_time
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.1.0"}