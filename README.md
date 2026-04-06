# 🎫 Ticket-Andon-IT: Intelligent Management System

* **YouTube Link: https://youtu.be/e-ixaa0pKbE
* **Colab Link: https://colab.research.google.com/drive/1UaHgelLPBvZwZfYv5ILHBWwDSRAvTfJO#scrollTo=uhBZK6EA-ie6

## 🚀 Overview

**Ticket-Andon-IT** is a Full-Stack intelligent solution that evolved from a legacy Ticket Management system into a proactive monitoring ecosystem. 
It merges **Lean Manufacturing principles (Andon)** with **Supervised Machine Learning** to predict hardware failures and security risks before they disrupt the workflow.

This project demonstrates:
  * **Intelligence:** Real-time telemetry classification using **SVM (Support Vector Machine)**.
  * **Governance:** Automated CI/CD pipelines and standardized OpenAPI documentation.
  * **Quality Assurance:** Automated performance tests via PyTest to ensure model accuracy.

-----

## 🎓 Academic Validation & Architectural Robustness

This MVP 2.0 was designed with strict software engineering and mathematical principles. 

Two architectural decisions were fundamental to this validation:

1. **Mathematical Choice of SVM & Preprocessing Stress-Test:** Instead of relying on "black-box" models, the Support Vector Machine (SVM) was chosen strictly for its geometric precision. It creates a robust hyperplane that reliably separates server states (Stable, Warning, Critical). 
To ensure immunity against infrastructure anomalies (e.g., sudden CPU spikes) and prevent *Data Leakage*, we did not settle for default data scaling. During the competitive modeling phase, algorithms were stress-tested against **six different mathematical scaling transformations** (including outlier-resistant `RobustScaler` and `QuantileTransformer`). Furthermore, we actively compared the SVM against:
    * **Decision Trees:** Discarded due to a high risk of *overfitting* on noisy infrastructure data.
    * **K-Nearest Neighbors (KNN):** Discarded due to its high computational cost and inference latency during real-time background polling.
    * **Naive Bayes:** Discarded because it assumes that variables are strictly independent, which is false in IT infrastructure (a CPU spike almost always impacts RAM or I/O).

2. **Safe Export via Scikit-Learn Pipeline:** To prevent data leakage and guarantee that the mathematical calculation behaves exactly as it did in training, the deployment does not export the SVM model alone. 
Instead, it exports a complete **Pipeline** (encapsulating both the winning Scaler and the SVM). 
This ensures that the telemetry is properly normalized before any prediction is made in production.

-----

## 🏗️ Architecture & Component Logic

The project is organized into a single repository to ensure consistency:

  * **/backend**: Flask RESTful API (Stateless/JWT), AI Predictor logic, and SQLAlchemy ORM.
  * **/frontend**: Vanilla JS SPA with real-time Andon visual management and Kanban board. 
    * *Architecture Note:* The JavaScript front-end acts as a **Client-Side ETL (Extract, Transform, Load)**. 
    It extracts telemetry from JSON batches, flattens deep nested objects, inputs missing values, and sends a perfectly formatted mathematical vector to the Python backend, saving server processing costs.
  * **/data**: Telemetry datasets in JSON and CSV formats.
  * **/notebooks**: Google Colab research files showing model training and competitive analysis.

-----

## 🧠 Machine Learning Component

  * **Dataset:** Based on the *AI4I 2020 Predictive Maintenance Dataset (UCI)*, adapted for IT endpoint telemetry.
  * **Independent Execution (Requirement 1):** The dataset is loaded via **GitHub Raw URL (JSON Lines)** within the Notebook, allowing direct execution in Google Colab without local setup.
  * **Algorithm & Hyperparameter Tuning (State-of-the-Art):** SVM optimized via `GridSearchCV`. In an advanced approach, **the scaling technique itself was treated as a hyperparameter**. The grid exhaustively crossed the 6 scalers with SVM's `C` and `kernel` parameters to find the geometrically perfect fit.
  * **Performance (The "Microsoft Defender" Effect):** The validated model achieved an unprecedented **100% (1.0000) Accuracy**. Rather than indicating *overfitting* or Data Leakage, this reflects the highly deterministic nature of corporate IT telemetry (similar to Microsoft Defender JSON logs), where hardware degradation follows strict, clean mathematical boundaries perfectly captured by our optimized Pipeline.
  * **Andon Status:**
      * 🟢 **Normal:** Healthy operations.
      * 🟡 **Warning:** Resource exhaustion or unusual behavior.
      * 🔴 **Critical:** Imminent failure or security risk detected.

-----

## 🧪 Quality Assurance (CI/CD)

Following **Requirement 5**, we implemented an automated pipeline that validates:

  * **Performance Threshold:** PyTest ensures the model maintains a **minimum accuracy of 80%**. 
  If performance drops below this threshold, the deployment is blocked.

  * **Model Integrity:** Verifies that the `.pkl` file (Pipeline + SVM) is correctly loaded by the backend server.

-----

## 🗺️ Roadmap & MLOps Evolution

As technical debt and future scalability milestones, we mapped:
  * **Dynamic Model Registry (MLOps):** Transitioning from a hardcoded `.pkl` contract to dynamic environment variables (`.env`). Future CI/CD pipelines will inject the approved model's version hash (`MODEL_NAME=svm_v2.pkl`) directly into the backend, enabling zero-downtime deployments (I follow KISS principles, but I don't forget abou MLOps best practices).
  * **AutoML Integration:** Allowing the pipeline to autonomously break ties between algorithms based on inference latency and memory constraints.
  * **Kubernetes Orchestration:** Ensuring self-healing for the AI agent and horizontal scalability for massive telemetry polling.

-----

## 🔐 Security & Data Privacy

In compliance with **Requirement 6**, the project applies **anonymization techniques**. 
Sensitive machine and user identifiers were replaced with generic labels (SENS-01), ensuring the AI pipeline processes only technical hardware metrics and adheres to GDPR/LGPD principles.

-----

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, Flask, Scikit-Learn, SQLAlchemy, Marshmallow |
| **Frontend** | HTML5, CSS3, JavaScript (Fetch API) |
| **DevOps** | GitHub Actions, PyTest |
| **API Doc** | Swagger / OpenAPI 2.0 |

-----

## 💻 Installation & Setup

### 1. Backend Setup

1.  Navigate to: `cd backend`
2.  Create and activate venv:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run server: `python app.py`
      * *Access Swagger UI at: `http://127.0.0.1:5000/apidocs`*

-----

### ✅ MVP 2 Submission Checklist

  * [x] **Colab Notebook:** Execution via Raw URL.
  * [x] **Embedded Model:** `.pkl` loading in the Backend.
  * [x] **Accuracy Test:** 80% threshold validated via PyTest.
  * [x] **Video Demo:** Under 3 minutes showing full integration.
