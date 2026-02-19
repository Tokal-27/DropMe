"""
Data ingestion module for waste classification pipeline
Handles real-time data from IoT devices and batch uploads
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RealTimeDataIngestion:
    """Handles real-time data streaming from IoT devices"""
    
    def __init__(self, kafka_broker: str = "kafka:9092", topic: str = "waste-classification-raw"):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.records_ingested = 0
        logger.info(f"Initialized real-time ingestion from {kafka_broker}/{topic}")
    
    def ingest_stream(self, max_records: int = None):
        """
        Consume records from Kafka stream
        In production, uses actual Kafka consumer
        """
        logger.info("Starting stream consumption...")
        
        # Simulated stream data
        sample_records = self._generate_sample_records()
        
        for i, record in enumerate(sample_records[:max_records] if max_records else sample_records):
            self.records_ingested += 1
            yield record
            
            if (i + 1) % 100 == 0:
                logger.info(f"Ingested {i + 1} records")
    
    def _generate_sample_records(self) -> List[Dict]:
        """Generate sample records for demo purposes"""
        import base64
        import numpy as np
        
        records = []
        materials = ["plastic", "metal", "glass", "organic", "paper", "electronic"]
        devices = ["machine_001", "machine_002", "machine_003"]
        
        for i in range(100):
            # Simulate image data
            fake_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            image_bytes = fake_image.tobytes()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            record = {
                "device_id": np.random.choice(devices),
                "timestamp": datetime.now().isoformat(),
                "image_base64": image_b64[:100],  # Truncated for demo
                "image_metadata": {
                    "width": 224,
                    "height": 224,
                    "format": "jpeg",
                    "quality": 95
                },
                "environmental_data": {
                    "temperature": np.random.uniform(20, 25),
                    "humidity": np.random.uniform(40, 60),
                    "lighting": np.random.uniform(700, 900)
                },
                "machine_status": {
                    "operational": True,
                    "belt_speed": np.random.uniform(1.0, 2.0),
                    "camera_angle": 45
                }
            }
            records.append(record)
        
        return records


class BatchDataIngestion:
    """Handles batch data ingestion from cloud storage"""
    
    def __init__(self, storage_type: str = "s3", bucket_name: str = "waste-classification-data"):
        self.storage_type = storage_type
        self.bucket_name = bucket_name
        self.records_ingested = 0
        logger.info(f"Initialized batch ingestion from {storage_type}/{bucket_name}")
    
    def ingest_batch(self, date: str = None, max_records: int = None):
        """
        Ingest batch data for specific date
        In production, reads from S3/GCS
        """
        date = date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Starting batch ingestion for {date}...")
        
        # Simulated batch reading
        records = self._read_batch_from_storage(date)
        
        for i, record in enumerate(records[:max_records] if max_records else records):
            self.records_ingested += 1
            yield record
        
        logger.info(f"Batch ingestion complete: {self.records_ingested} records")
    
    def _read_batch_from_storage(self, date: str) -> List[Dict]:
        """Simulate reading batch from storage"""
        # In production: actual S3/GCS API calls
        return [{"type": "batch_record", "date": date} for _ in range(50)]
