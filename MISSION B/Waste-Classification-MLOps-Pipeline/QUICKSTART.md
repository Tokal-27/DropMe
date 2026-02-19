# Waste Classification MLOps Pipeline - Quick Start

## System Requirements

- Python 3.9+
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- 2 CPU cores minimum

## Installation

### 1. Clone the project
```bash
cd Waste-Classification-MLOps-Pipeline
```

### 2. Create Python environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r api/requirements.txt
pip install -r model/requirements.txt
pip install -r monitoring/requirements.txt
pip install -r data_pipeline/requirements.txt
pip install -r tests/requirements.txt
```

## Local Development

### Run API only
```bash
python api/app.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Run with Docker Compose (recommended)
```bash
cd docker
docker-compose up --build
```

Services available at:
- **API**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Run tests
```bash
pytest tests/ -v --cov=api --cov=model
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Make a Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "test_image.jpg",
    "material": "plastic",
    "confidence_threshold": 0.7
  }'
```

### Batch Prediction
```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '["plastic", "metal", "glass"]'
```

### Get Metrics
```bash
curl http://localhost:8000/metrics
```

## Deployment

### Local Deployment
```bash
bash scripts/deploy.sh
```

### Health Check
```bash
bash scripts/health_check.py health
```

### Monitor Continuously
```bash
bash scripts/health_check.py monitor
```

### View Metrics
```bash
bash scripts/health_check.py metrics
```

## Monitoring

### Prometheus Queries
```
# API request rate
rate(http_requests_total[1m])

# API latency
histogram_quantile(0.95, http_request_duration_seconds)

# Model predictions
increase(predictions_total[5m])
```

### Grafana Dashboards
Available at `http://localhost:3000`
- Model Performance Dashboard
- System Health Dashboard
- Drift Detection Dashboard

## Configuration

### Environment Variables
```bash
# .env file
ENVIRONMENT=production
API_PORT=8000
API_WORKERS=4
MONITORING_ENABLED=true
DRIFT_DETECTION_ENABLED=true
CONFIDENCE_THRESHOLD=0.7
DRIFT_ALERT_THRESHOLD=0.3
FAILURE_ALERT_THRESHOLD=0.05
```

## Production Checklist

- [ ] Configure secrets in CI/CD (API keys, deployment credentials)
- [ ] Set up monitoring alerts
- [ ] Configure log aggregation (ELK/Splunk)
- [ ] Set up database backups
- [ ] Enable HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up horizontal scaling
- [ ] Plan disaster recovery
- [ ] Document runbooks

## Troubleshooting

### API won't start
```bash
# Check port is not in use
lsof -i :8000

# Check logs
docker-compose logs api
```

### Model drift alerts
```bash
# Check recent predictions
curl http://localhost:8000/metrics/detailed | jq '.drift_detection'

# View drift history
cat logs/alerts.log | grep "drift"
```

### High latency
```bash
# Check resource usage
docker stats

# Check model loading
curl http://localhost:8000/model-info
```

## Next Steps

1. **Customize the model**: Replace simulated inference with real model
2. **Connect data pipeline**: Integrate Kafka/IoT data sources
3. **Add authentication**: Implement JWT tokens
4. **Configure alerts**: Set up Slack/PagerDuty notifications
5. **Scale infrastructure**: Deploy to Kubernetes
6. **Add dashboard**: Customize Grafana dashboards

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design
- [Production Risks](docs/PRODUCTION_RISKS.md) - Risk analysis
- [Data Pipeline](docs/DATA_PIPELINE.md) - Data architecture

## Support

For issues and questions, check:
- [GitHub Issues](https://github.com/your-org/waste-classifier/issues)
- [Documentation](docs/)
- [Logs](logs/)

---

**Last Updated**: February 2026
**Version**: 1.0.0
