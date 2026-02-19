# 🏭 OPERATIONS & ESG OBSERVABILITY STACK (Monitoring & System Thinking)

## 🎯 Project Overview
This project demonstrates a robust, containerized observability stack designed for an industrial context. It goes beyond traditional monitoring by integrating **ESG (Environmental, Social, and Governance)** metrics, ensuring that machine operations are not only efficient but also sustainable and auditable.

---

## 🏗️ System Architecture & Components
The system utilizes a modular "Producer-Collector-Visualizer" pattern:

1. **Telemetry Generator (Python/Edge)**: 
   - Simulates an IoT-enabled industrial machine.
   - Produces real-time signals: `Uptime`, `Temperature`, `Energy Consumption`, and `Error Codes`.
2. **Collection Service (Prometheus)**: 
   - Acting as a **Time-Series Database (TSDB)**.
   - Scrapes metrics every 5 seconds, ensuring high-resolution historical data.
3. **Observability Layer (Grafana)**: 
   - Translates raw metrics into actionable business and environmental insights.

<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-40-38" src="https://github.com/user-attachments/assets/4cf3f425-12b7-443b-9d0f-7b1684a89aa1" />
<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-39-55" src="https://github.com/user-attachments/assets/400c2552-1ef2-4b37-b6d8-6b6c5677438c" />
<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-39-50" src="https://github.com/user-attachments/assets/01ed2b39-6682-4405-bb20-2d4460119329" />
<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-38-06" src="https://github.com/user-attachments/assets/3372689f-1825-44ac-ae0b-2f4c84242092" />

---

## 🚀 Deployment & Troubleshooting

### 1. Prerequisites
- Docker & Docker Compose.
- **Port Management**: The system is configured to use Port **3001** for Grafana to avoid common conflicts with local instances on Port 3000.

### 2. Quick Start
```bash
# Clean up any conflicting containers
docker rm -f $(docker ps -aq)

# Build and start the stack
docker-compose up --build -d


3. Access Ports

    Grafana Dashboard: http://localhost:3001 (User: admin / Pass: admin)

    Prometheus UI: http://localhost:9090

    Machine Metrics (Raw): http://localhost:8000

📊 Monitoring & ESG Queries (PromQL)
🌿 ESG & Sustainability (The "E" in ESG)

To make metrics auditable, we use calculated fields to show environmental impact:

    Carbon Footprint (kg CO2):
    esg_energy_kwh_total * 0.4
    Logic: Converts raw energy data into CO2 emissions using a verifiable conversion factor.

    Energy Consumption Trend:
    sum(esg_energy_kwh_total)

⚙️ Operational Health & Efficiency

    Machine Temperature Monitoring:
    machine_temperature
    Visualization: Use Time Series with Thresholds (Red > 90°C) for Anomaly Detection.

    System Uptime Integrity:
    avg_over_time(machine_status[1h]) * 100
    Audit Logic: Provides a percentage of operational availability to ensure reporting honesty.

🛡️ ESG Traceability Concept
Auditability Fields

By capturing machine_id alongside energy_kwh and a precise timestamp, we create a "Digital Twin" of the machine's impact. This makes the recycling or production process transparent for third-party auditors.
Data Integrity & Greenwashing Prevention

    Immutable Timestamps: Prometheus records data in an append-only format. This prevents "Greenwashing" because historical pollution or energy spikes cannot be deleted or edited.

    Handling Missing Data: Gaps in telemetry (No Data) are explicitly visible. In ESG auditing, a "Data Gap" is treated as a failure in governance, forcing transparency.

📝 Final Insights & Future Roadmap
🔴 The Weakest Point

The current system's weakest point is Static Infrastructure Dependencies. As identified during deployment, port conflicts (e.g., Port 8000 or 3000 being occupied) can halt observability.

    Solution: Future iterations should use a Reverse Proxy (Nginx) or Service Discovery to handle dynamic port allocation.

🔮 Predictive Maintenance (Next Step)

We can evolve this stack from Reactive to Proactive by adding a Machine Learning sidecar container:

    Trend Analysis: Analyze the temperature gradient (Rate of increase).

    Alerting: If the temperature is predicted to hit 95°C based on current acceleration, trigger an alert 10 minutes before the failure happens.

    ESG Impact: Predictive maintenance reduces "Waste Units" caused by sudden machine failure, further improving ESG scores.



    
