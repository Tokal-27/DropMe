# Waste Classification MLOps Deployment Pipeline

A comprehensive production-ready MLOps pipeline for waste material classification with monitoring, CI/CD automation, and containerization.

## Overview

This project demonstrates how a waste classification model can be deployed, monitored, and maintained in production with:
- ✅ Containerized inference service (Docker + FastAPI)
- ✅ CI/CD pipeline with versioning & rollback (GitHub Actions)
- ✅ Real-time monitoring for model drift and prediction failures
- ✅ Production-grade architecture and documentation

## Project Structure

```
Waste-Classification-MLOps-Pipeline/
├── model/               # Waste classification model
├── api/                 # FastAPI inference service
├── docker/              # Docker configuration
├── monitoring/          # Model monitoring & drift detection
├── scripts/             # Deployment & health check scripts
├── tests/               # Unit and integration tests
├── data_pipeline/       # Data ingestion from machines
├── docs/                # Architecture & risk documentation
└── .github/workflows/   # CI/CD pipelines
```

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Local Development

1. **Clone and setup**
```bash
cd Waste-Classification-MLOps-Pipeline
pip install -r api/requirements.txt
```

2. **Run the API**
```bash
python api/app.py
```

3. **Test the endpoint**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"image_path": "test_image.jpg", "material": "plastic"}'
```

### Docker Deployment

```bash
cd docker
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /predict
Classify waste material from image or prediction data.

**Request:**
```json
{
  "image_path": "waste_image.jpg",
  "material": "plastic",
  "confidence_threshold": 0.7
}
```

**Response:**
```json
{
  "predicted_class": "plastic",
  "confidence": 0.95,
  "model_version": "v1.0.0",
  "inference_time_ms": 45,
  "prediction_id": "pred_12345"
}
```

### GET /health
Health check endpoint.

### GET /metrics
Get current model performance metrics.

## Monitoring

The pipeline includes real-time monitoring for:
- **Model Drift Detection**: Tracks distribution changes in predictions
- **Prediction Failures**: Alerts on failed classifications
- **Performance Metrics**: Accuracy, latency, throughput
- **Data Quality**: Input validation and anomalies

Metrics feed the **AI Waste Intelligence Dashboard** for visualization.

## CI/CD Pipeline

The GitHub Actions workflows handle:
- **Testing**: Unit & integration tests on each push
- **Building**: Docker image creation & ECR push
- **Versioning**: Automatic semantic versioning
- **Rollback**: Quick rollback mechanism for failed deployments

See `.github/workflows/` for pipeline configurations.

## Production Risks & Mitigations

See [PRODUCTION_RISKS.md](docs/PRODUCTION_RISKS.md) for:
- Model degradation & drift
- Data quality issues
- Infrastructure failures
- Security concerns
- Mitigation strategies

## Data Pipeline

See [DATA_PIPELINE.md](docs/DATA_PIPELINE.md) for:
- Data ingestion from waste classification machines
- Real-time stream processing
- Data validation & quality checks
- Feature engineering pipeline

## Documentation

- [Architecture Diagram](docs/ARCHITECTURE.md) - System design & components
- [Production Risks](docs/PRODUCTION_RISKS.md) - Risk assessment & mitigation
- [Data Pipeline](docs/DATA_PIPELINE.md) - Data ingestion requirements

## Performance Metrics

- **Inference Latency**: ~50ms per prediction
- **Throughput**: 100+ requests/sec
- **Model Accuracy**: 95%+ on validation set
- **Uptime Target**: 99.9%

## Contributing

1. Create a feature branch
2. Make changes and add tests
3. Push to GitHub
4. Create PR - CI/CD will run tests
5. Merge and auto-deploy to staging

## Deployment Versions

Current versions:
- **API Version**: v1.0.0
- **Model Version**: v1.0.0
- **Schema Version**: 1.0

## Support & Monitoring

- View logs: `scripts/health_check.py`
- Monitor metrics: Prometheus + Grafana (configured in docker-compose)
- Rollback: `scripts/rollback.sh <version>`

---

**Last Updated**: February 2026
**Maintained By**: MLOps Team
