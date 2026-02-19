## 1. Alternatives Rejected
* **AWS Lambda (Serverless):** Rejected for the inference layer due to "cold start" latency. Real-time mechanical sorting at edge devices requires the consistent response times provided by containerized microservices (Docker/FastAPI).
* **Heavy ML Serving Frameworks (TorchServe):** Overkill for this simulation. FastAPI provides the necessary asynchronous capabilities and high performance for wrapping simple inference logic without unnecessary overhead.





## 2. Biggest Technical Risk
* **Data Drift & Payload Overload:** The physical appearance of waste changes over time. Without an automated retraining loop based on physical "Ground Truth" feedback, the model's accuracy will silently degrade in production. Additionally, synchronous payload overload (sending raw images directly to the API) risks memory exhaustion.





## 3. What I would improve first in production
1. **Infrastructure as Code (IaC):** I would implement **Terraform** modules to provision the underlying infrastructure (e.g., AWS ECS, Load Balancers) to ensure the environment is reproducible and version-controlled.
2. **Event-Driven Architecture:** Introduce a message queue (like **AWS SQS**) between the edge device and the inference API. The device drops the image in S3 and triggers a queue message, preventing traffic spikes from overwhelming the service.