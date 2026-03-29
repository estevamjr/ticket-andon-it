# 🎫 Ticket-Andon-IT: Intelligent Management System

[](https://www.google.com/search?q=https://github.com/estevamjr/ticket-andon-it/actions)

## 🚀 Overview

**Ticket-Andon-IT** is a Full-Stack intelligent solution that evolved from a legacy Ticket Management system into a proactive monitoring ecosystem. It merges **Lean Manufacturing principles (Andon)** with **Supervised Machine Learning** to predict hardware failures and security risks before they disrupt the workflow.

This project demonstrates:

  * **Evolution:** Refactoring a CRUD-based MVP into an AI-driven system.
  * **Intelligence:** Real-time telemetry classification using **SVM (Support Vector Machine)**.
  * **Governance:** Automated CI/CD pipelines and standardized OpenAPI documentation.

-----

## 🏗️ Monorepo Architecture

The project is organized into a single repository to ensure consistency across the entire stack:

  * **/backend**: Flask RESTful API (Stateless/JWT), AI Predictor logic, and SQLAlchemy ORM.
  * **/frontend**: Vanilla JS SPA (No frameworks) with real-time Andon visual management and Kanban board.
  * **/data**: JSON telemetry datasets, including the **AI4I 2020 Predictive Maintenance** source from UCI.
  * **/notebooks**: Google Colab research files showing model training and hyperparameter tuning.

-----

## 🧠 Machine Learning Component

  * **Dataset:** [AI4I 2020 Predictive Maintenance Dataset (UCI)](https://www.google.com/search?q=https://archive.ics.uci.edu/dataset/544/ai4i%2B2020%2Bpredictive%2Bmaintenance%2Bdataset).
  * **Algorithm:** SVM (Support Vector Machine) optimized via GridSearchCV.
  * **Goal:** Multiclass classification of hardware health:
      * 🟢 **Normal:** Healthy operations.
      * 🟡 **Warning:** Resource exhaustion or unusual behavior.
      * 🔴 **Critical (Andon):** Imminent failure or security risk detected.
  * **Deployment:** Model serialized with `joblib` for real-time inference in the Flask backend.

-----

## 🛠️ Tech Stack & Requirements

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, Flask, Scikit-Learn, SQLAlchemy, Marshmallow |
| **Frontend** | HTML5, CSS3, JavaScript (Pure/Fetch API) |
| **DevOps** | GitHub Actions (CI/CD), PyTest |
| **API Doc** | Swagger / OpenAPI 2.0 (English Standard) |

-----

## 💻 Installation & Setup

### 1\. Backend Setup

1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server:
    ```bash
    python app.py
    ```
    *Access Swagger UI at: `http://127.0.0.1:5000/apidocs`*

### 2\. Frontend Setup

1.  No installation required.
2.  Simply open `frontend/index.html` in any modern web browser.
3.  Ensure the Backend is running to enable real-time AI updates.

-----

## 🧪 Quality Assurance (CI/CD)

The project includes an automated **GitHub Action** that triggers on every push. It validates:

  * Code indentation and PEP8 compliance.
  * Unit tests for the AI Predictor and API endpoints.
  * Model availability and integrity.

-----

## 📄 Refactoring Notes (MVP 1 to MVP 2)

As part of the evolution for the *Intelligent Systems Engineering* course, I have personally:

1.  **Refactored** the entire directory structure into a Monorepo.
2.  **Standardized** all documentation, variable names, and Swagger definitions to **English**.
3.  **Fixed** indentation and code styling issues across all `.py` and `.js` files.
4.  **Integrated** the SVM prediction logic into the legacy ticket services.
