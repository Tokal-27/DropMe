# DropMe Project Documentation

Mission B – MLOps Deployment Pipeline (AI Infrastructure Focus)

This project demonstrates how a waste classification model can be deployed and monitored in production using MLOps principles. A simulated inference service exposes an API endpoint that returns material predictions, and the service is containerized for consistent deployment locally or in the cloud. A CI/CD workflow (e.g., via GitHub Actions) manages automated builds, versioning, and rollback strategies. Monitoring tracks failed predictions, performance metrics, and potential model drift to feed an AI Waste Intelligence Dashboard. The documentation includes an architecture diagram, production risk analysis, and required machine data pipelines to ensure reliable, scalable AI operations.


Misson C :Operations & ESG Observability Stack (Monitoring & System Thinking Focus)

This project demonstrates how machine health, uptime, and ESG impact metrics can be tracked and made auditable through a structured observability stack. A telemetry generator simulates machine signals such as uptime, transactions, temperature, and error codes, which are collected by a service that stores timestamped data for traceability. An observability layer—using tools like Prometheus and Grafana—visualizes machine status, event counts, and anomalies such as sudden downtime. The ESG traceability model defines required audit fields, explains the impact of missing or duplicate data on reporting accuracy, and ensures metric integrity through immutable time-series storage. Documentation includes the system architecture, identified weak points, and a roadmap for adding predictive maintenance capabilities in future iterations.

## Missions

The main missions of the DropMe project are:
- **Ease of Access**: Provide a simple interface for users to manage their drop-off tasks.
- **Automation**: Automate the processes involved to minimize manual efforts.
- **Scalability**: Ensure the application can handle growing user requirements efficiently.

## Technology Stack

The technology stack used in the DropMe project includes:
- **Python** (89.8%): The primary programming language for developing the application logic.
- **Dockerfile** (10.2%): For containerizing the application and ensuring consistency across different environments.


