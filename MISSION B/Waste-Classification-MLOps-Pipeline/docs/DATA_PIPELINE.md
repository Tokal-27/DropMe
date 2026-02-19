# Data Pipeline Architecture & Requirements

## Overview

The data pipeline is responsible for ingesting real-time data from waste classification machines, processing it, validating quality, and feeding it to the ML model for inference.

---

## 1. Data Sources

### 1.1 Primary Data Source: Waste Classification Machines

**Device Type**: IoT Sensors on waste sorting/classification lines

**Data Stream Characteristics**:
- **Format**: Real-time JSON over HTTP/MQTT
- **Frequency**: 1-10 events per second per machine
- **Payload Size**: 100-500 KB per event (image data)
- **Latency Requirement**: < 100ms for inference

**Data Fields**:
```json
{
  "device_id": "machine_001",
  "timestamp": "2026-02-19T14:30:45Z",
  "image_base64": "iVBORw0KGgoAAAANS...",
  "image_metadata": {
    "width": 224,
    "height": 224,
    "format": "jpeg",
    "quality": 95
  },
  "environmental_data": {
    "temperature": 22.5,
    "humidity": 45,
    "lighting": 800
  },
  "machine_status": {
    "operational": true,
    "belt_speed": 1.5,
    "camera_angle": 45
  }
}
```

### 1.2 Alternative Data Sources

**Batch Uploads** (for model retraining)
- S3/GCS bucket with historical images
- Frequency: Daily/weekly batches
- Used for model retraining and validation

**User Submissions** (for feedback loop)
- Web interface for manual classification
- Used to collect ground truth labels
- Helps identify model errors

---

## 2. Data Ingestion Architecture

### 2.1 Streaming Ingestion

```
IoT Devices (Kafka Producer)
    ↓
Kafka Topic: waste-classification-raw
    ↓
Kafka Consumer (Python)
    ↓
Message Queue (Redis)
    ↓
Processing Workers
    ↓
Validation & Enrichment
```

**Configuration**:
```python
# In data_pipeline/data_ingestion.py
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "waste-classification-raw"
KAFKA_CONSUMER_GROUP = "waste-classifier-group"
BATCH_SIZE = 32
INGESTION_LATENCY_SLA = 100  # milliseconds
```

### 2.2 Batch Ingestion

```python
# For historical data
import boto3
from datetime import datetime, timedelta

class BatchDataIngestion:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'waste-classification-data'
    
    def ingest_daily_batch(self, date: str):
        """Ingest daily batch from S3"""
        prefix = f"raw/{date}/"
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        
        for obj in response.get('Contents', []):
            image_key = obj['Key']
            # Download and process
            self.process_image(image_key)
```

---

## 3. Data Processing Pipeline

### 3.1 Preprocessing Steps

```
Raw Image
    ↓
1. Format Validation
   - Check JPEG/PNG format
   - Verify dimensions (224x224 or resize)
   - Check file integrity
    ↓
2. Image Enhancement
   - Normalize pixel values (0-1)
   - Contrast enhancement
   - Augmentation (for robustness)
    ↓
3. Feature Extraction
   - CNN feature embedding
   - Dimensionality reduction
   - Normalization
    ↓
4. Metadata Enrichment
   - Add environmental context
   - Add machine metadata
   - Add timestamp info
    ↓
Processed Features
```

**Implementation**:
```python
# In data_pipeline/data_processing.py
import cv2
import numpy as np

class DataProcessor:
    def __init__(self):
        self.target_size = (224, 224)
        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
    
    def preprocess_image(self, image_array):
        """Preprocess image for model input"""
        # Resize
        image = cv2.resize(image_array, self.target_size)
        
        # Normalize
        image = image.astype(np.float32) / 255.0
        image = (image - self.mean) / self.std
        
        return image
    
    def validate_image_quality(self, image_array):
        """Check image quality metrics"""
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(image_array, cv2.CV_64F).var()
        
        # Brightness (mean pixel value)
        brightness = np.mean(image_array)
        
        # Check thresholds
        if laplacian_var < 50:  # Too blurry
            raise ValueError("Image too blurry")
        if brightness < 30 or brightness > 225:
            raise ValueError("Image too dark or too bright")
        
        return True
```

### 3.2 Feature Engineering

**Features Extracted**:
- Color histograms
- Texture features (Gabor filters)
- Shape features (contours)
- Edge density
- Spatial frequency features

**Feature Normalization**:
- StandardScaler (zero mean, unit variance)
- Min-max scaling for specific features
- Log transformation for skewed features

---

## 4. Data Validation

### 4.1 Input Validation Pipeline

```python
class DataValidator:
    def validate_record(self, record: dict) -> Tuple[bool, str]:
        """Validate incoming data record"""
        
        # 1. Required fields check
        required_fields = ['device_id', 'timestamp', 'image_base64']
        for field in required_fields:
            if field not in record:
                return False, f"Missing field: {field}"
        
        # 2. Data type validation
        if not isinstance(record['timestamp'], str):
            return False, "Timestamp must be ISO format string"
        
        # 3. Image validation
        try:
            image_data = base64.b64decode(record['image_base64'])
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                return False, "Invalid image data"
        except Exception as e:
            return False, f"Image decode error: {str(e)}"
        
        # 4. Value range validation
        if len(record['device_id']) == 0 or len(record['device_id']) > 50:
            return False, "Invalid device_id format"
        
        return True, "Valid"
```

### 4.2 Data Quality Metrics

**Quality Checks**:
- ✅ Completeness: All required fields present
- ✅ Validity: Data types and formats correct
- ✅ Consistency: Values within expected ranges
- ✅ Accuracy: Cross-validation against known patterns
- ✅ Timeliness: Data within acceptable age

**Thresholds**:
```python
DATA_QUALITY_THRESHOLDS = {
    "completeness": 0.98,      # 98% fields present
    "validity": 0.99,          # 99% valid formats
    "consistency": 0.95,       # 95% expected ranges
    "freshness": 300,          # 5 minute max age
    "duplicate_rate": 0.01     # Max 1% duplicates
}
```

### 4.3 Anomaly Detection

**Anomalies Detected**:
- Sudden distribution shifts in image properties
- Unusual combinations of metadata
- Outlier values in sensor readings
- Duplicate or near-duplicate images

**Detection Method**:
```python
class AnomalyDetector:
    def detect_anomalies(self, record: dict) -> bool:
        """Detect anomalous records"""
        
        # Statistical anomaly detection
        brightness = np.mean(self.current_image)
        historical_brightness = self.get_recent_brightness_distribution()
        
        if brightness > np.mean(historical_brightness) + 3 * np.std(historical_brightness):
            return True  # Anomalous
        
        return False
```

---

## 5. Data Storage Architecture

### 5.1 Raw Data Storage

**Location**: S3/GCS bucket
**Format**: Original image + metadata JSON
**Retention**: 90 days
**Organization**:
```
s3://waste-classification-raw/
├── 2026/02/19/
│   ├── machine_001/
│   │   ├── 14_30_45_UUID.jpg
│   │   └── 14_30_45_UUID.json
│   └── machine_002/
```

### 5.2 Processed Data Storage

**Location**: PostgreSQL database
**Schema**:
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    prediction_id UUID,
    predicted_class VARCHAR(50),
    confidence FLOAT,
    inference_time_ms INT,
    timestamp TIMESTAMP,
    environment_temp FLOAT,
    environment_humidity FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ground_truth (
    id SERIAL PRIMARY KEY,
    prediction_id UUID UNIQUE,
    actual_class VARCHAR(50),
    label_confidence FLOAT,
    labeled_by VARCHAR(100),
    labeled_at TIMESTAMP
);
```

### 5.3 Feature Store (Future Enhancement)

```python
# Planned feature store integration
from tecton import Entity, Dataset, FS

waste_material = Entity(
    name="waste_material",
    description="Waste material being classified"
)

class MaterialFeatures(Dataset):
    entity = waste_material
    
    @feature_view
    def shape_features(self):
        return {
            "perimeter": float,
            "area": float,
            "compactness": float
        }
    
    @feature_view
    def color_features(self):
        return {
            "dominant_color": str,
            "color_histogram": list
        }
```

---

## 6. Real-time Data Streaming Requirements

### 6.1 Event Streaming Platform

**Recommended**: Apache Kafka

**Configuration**:
```yaml
Topic: waste-classification-raw
Partitions: 10 (by device_id)
Replication Factor: 3
Retention: 7 days
Compression: snappy

Topic: waste-classification-processed
Partitions: 20
Replication Factor: 3
```

### 6.2 Stream Processing Pipeline

```python
# Using Python Kafka Consumer
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'waste-classification-raw',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='waste-classifier-group',
    auto_offset_reset='earliest'
)

for message in consumer:
    record = message.value
    
    # Validate
    is_valid, error = validator.validate_record(record)
    if not is_valid:
        # Handle validation error
        continue
    
    # Process
    processed_data = processor.process(record)
    
    # Infer
    prediction = model.predict(processed_data)
    
    # Store result
    store_prediction(prediction)
    
    # Check for drift
    drift_detector.update(prediction)
```

---

## 7. Data Pipeline Monitoring

### 7.1 Metrics to Track

**Ingestion Metrics**:
- Records per second
- Ingestion latency (p50, p95, p99)
- Message queue depth
- Kafka consumer lag

**Processing Metrics**:
- Processing latency per record
- Validation failure rate
- Anomaly detection rate
- Feature extraction time

**Quality Metrics**:
- Data completeness (%)
- Data validity (%)
- Duplicate rate (%)
- Schema validation failures

### 7.2 Monitoring Implementation

```python
from prometheus_client import Counter, Histogram

# Ingestion metrics
records_ingested = Counter(
    'records_ingested_total',
    'Total records ingested',
    ['source', 'device_id']
)

ingestion_latency = Histogram(
    'ingestion_latency_seconds',
    'Time to ingest record',
    buckets=[0.01, 0.05, 0.1, 0.5]
)

# Quality metrics
validation_failures = Counter(
    'validation_failures_total',
    'Records failed validation',
    ['reason']
)
```

---

## 8. End-to-End Data Flow Example

```
1. IoT Device captures image
   ↓ [timestamp: 14:30:45.123]
2. Sends to Kafka topic
   ↓ [latency: 50ms]
3. Consumer reads and validates
   ↓ [latency: 20ms]
4. Preprocesses image
   ↓ [latency: 30ms]
5. Extracts features
   ↓ [latency: 15ms]
6. Sends to model API
   ↓ [latency: 48ms]
7. Model returns prediction
   ↓ [confidence: 0.95]
8. Stores in database
   ↓ [latency: 5ms]
9. Updates drift detector
   ↓ [drift_score: 0.12]
10. Sends to sorting machine
    ↓ [total latency: 168ms]
```

**Total End-to-End Latency**: < 200ms ✅

---

## 9. Scaling Considerations

### 9.1 Current Capacity

- **Single instance**: 100 predictions/sec
- **Storage**: 10TB/month
- **Network bandwidth**: 1 Gbps

### 9.2 Scaling Strategy

**Horizontal Scaling**:
- Add more Kafka partitions
- Deploy multiple consumer instances
- Load balance API servers

**Vertical Scaling**:
- Increase machine specs (CPU, memory, GPU)
- Use faster storage (NVMe SSD)
- Optimize code for performance

**Data Archival**:
- Move old data to cold storage (Glacier)
- Compress historical logs
- Implement data retention policies

---

## 10. Disaster Recovery for Data Pipeline

**Backup Strategy**:
- Real-time replication to secondary region
- Daily snapshots of processed data
- Model checkpoint backups

**Recovery Time Objectives**:
- Kafka topic recovery: < 1 hour
- Database recovery: < 15 minutes
- Data reprocessing: < 4 hours

---

## Required Infrastructure

### Development Environment
```bash
Docker Compose stack:
- Kafka (single broker)
- PostgreSQL (development DB)
- Redis (caching)
```

### Production Environment
```
Kubernetes deployment:
- Kafka cluster (3+ brokers)
- PostgreSQL (HA with replication)
- Redis (HA with clustering)
- S3/GCS (object storage)
```

---

**Last Updated**: February 2026
**Version**: 1.0
**Status**: Ready for Implementation
