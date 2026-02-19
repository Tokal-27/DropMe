🏗️ System Architecture
📊 Monitoring & ESG Queries (PromQL)
🌿 ESG Impact Metrics

Carbon Footprint (kg CO₂):

esg_energy_kwh_total * 0.4

Energy Consumption Trend:

sum(esg_energy_kwh_total)
⚙️ Operational Health

Temperature Monitoring

machine_temperature

Threshold: > 90°C → anomaly

System Uptime Integrity

avg_over_time(machine_status[1h]) * 100

Provides operational availability percentage.

Downtime Detection

changes(machine_status[5m])
🛡️ ESG Traceability Concept
✅ Fields That Make Recycling Auditable

To ensure ESG-grade reporting, each record includes:

machine_id

timestamp

energy_kwh

transaction_count

error_code

These fields enable:

Traceability per machine

Historical reconstruction of environmental impact

Audit-ready reporting

⚠️ Duplicate or Missing Data Impact

Duplicate data inflates energy usage → false carbon reporting.

Missing telemetry creates ESG blind spots.

In ESG compliance, a "Data Gap" equals governance failure.

Observability makes both scenarios visible.

🔐 What Guarantees Metric Integrity?

Prometheus uses append-only time-series storage.

Historical metrics cannot be edited.

All anomalies remain historically visible.

Transparent calculation logic via PromQL.

This reduces the risk of ESG manipulation or greenwashing.

🔴 Identified Weakest Point
Static Infrastructure Dependencies

Fixed ports (3001, 8000, 9090)

Manual scaling

Single Prometheus instance

A port conflict or container crash can disrupt observability.

Future Improvement

Reverse proxy (e.g., Nginx)

Service discovery

Horizontal scaling

Remote storage backend

🔮 Predictive Maintenance Roadmap

The system can evolve from Reactive Monitoring to Proactive Intelligence by adding:

🤖 ML Sidecar Container

Capabilities:

Temperature gradient analysis (rate of increase)

Failure probability estimation

Early anomaly detection

Example Logic

If projected temperature ≥ 95°C within 10 minutes → trigger alert.

🌱 ESG Impact of Predictive Maintenance

Reduces unexpected machine failure

Minimizes wasted material batches

Improves uptime reporting accuracy

Lowers emergency energy spikes

This directly improves ESG performance metrics. 

shows 

<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-40-38" src="https://github.com/user-attachments/assets/414a7638-75c8-45bb-9756-24c2d37178d4" />

<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-39-55" src="https://github.com/user-attachments/assets/f3a744a6-115e-42a2-9dc4-4a210442f69a" />

<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-39-50" src="https://github.com/user-attachments/assets/fa3e5765-ecf9-4183-83d0-1898f207c244" />

<img width="1920" height="1080" alt="Screenshot from 2026-02-20 01-38-06" src="https://github.com/user-attachments/assets/7e5992e8-82ba-4f53-84b6-271ee8ff9ca0" />

