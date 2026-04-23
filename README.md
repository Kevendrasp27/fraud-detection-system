# Fraud Detection System

A production-ready Machine Learning web application that detects fraudulent financial transactions in real time, deployed on AWS with a full CI/CD pipeline.

**Made by KEVENDRA SINGH PARIHAR**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Machine Learning | Python, Scikit-learn (LogisticRegression + StandardScaler), Pandas |
| Experiment Tracking | MLflow |
| Backend API | FastAPI, Uvicorn, Pydantic |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Cloud | AWS S3, ECR, ECS Fargate, CloudWatch |

---

## Architecture

```
GitHub Push → GitHub Actions CI/CD
                ├── Run pytest tests
                ├── Build Docker image
                ├── Push to AWS ECR
                └── Deploy to AWS ECS Fargate
                        └── Container loads model from AWS S3 at startup
```

**Live URL:** `http://13.201.133.55:8000`

---

## Project Structure

```
fraud_detection/
├── app/
│   ├── main.py            # FastAPI app — routes, middleware, logging
│   ├── model_service.py   # Loads model from S3 (prod) or disk (local)
│   └── schemas.py         # Request/response data shapes (Pydantic)
├── model/
│   └── train.py           # ML training script + MLflow logging
├── frontend/
│   ├── index.html         # Glassmorphism UI
│   ├── style.css          # Styling + animations
│   └── script.js          # API calls + animated results
├── tests/
│   └── test_api.py        # pytest test suite (6 tests)
├── data/
│   └── paysim.csv         # Transaction dataset (not committed — add manually)
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions CI/CD pipeline
├── Dockerfile             # Production container (non-root user, healthcheck)
├── docker-compose.yml     # Local dev: API + MLflow + nginx frontend
├── nginx.conf             # Serves frontend via nginx
├── ecs-task-definition.json  # AWS ECS Fargate task config
└── requirements.txt       # Python dependencies
```

> **Note:** `model_artifacts/model.joblib` is not committed to git. In production, the model is loaded directly from AWS S3. For local development, train the model first (see below).

---

## Option 1 — Run Locally (without Docker)

### 1. Create and activate virtual environment

```bash
cd fraud_detection
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the model

```bash
venv\Scripts\python.exe model/train.py
```

> If `data/paysim.csv` is missing, the script auto-generates dummy data so you can test immediately. For real results, download the PaySim dataset from Kaggle (see below).

### 4. Start the backend API

```bash
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 5. Open the frontend

Open `frontend/index.html` directly in your browser.

### URLs

| Service | URL |
|---|---|
| API | http://127.0.0.1:8000 |
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

---

## Option 2 — Run with Docker (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Start all services

```bash
cd fraud_detection
docker-compose up --build
```

This starts 3 containers:
- **fraud-api** — FastAPI backend on port 8000
- **fraud-mlflow** — MLflow tracking UI on port 5001
- **fraud-frontend** — nginx serving the frontend on port 80

### URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:80 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| MLflow UI | http://localhost:5001 |

### Stop all services

```bash
docker-compose down
```

---

## Running Tests

```bash
cd fraud_detection
venv\Scripts\python.exe -m pytest tests/ -v
```

Tests cover:
- `/health` endpoint returns `200` with `status: ok`
- `/predict` returns valid structure (prediction + probability)
- Rejects negative amounts (`422`)
- Rejects missing fields (`422`)
- Rejects zero amounts (`422`)
- `/docs` (Swagger UI) is accessible

---

## How to Use the App

1. Open the frontend in your browser
2. Fill in the transaction details:
   - **Transaction Amount** — how much money is being sent
   - **Sender Balance Before** — sender's balance before the transaction
   - **Sender Balance After** — sender's balance after the transaction
   - **Receiver Balance Before** — receiver's balance before the transaction
   - **Receiver Balance After** — receiver's balance after the transaction
3. Click **Analyze Transaction**
4. The model returns **Safe** or **Fraud** with a confidence score

### Example Fraudulent Transaction (to test)

| Field | Value |
|---|---|
| Amount | 500000 |
| Sender Balance Before | 500000 |
| Sender Balance After | 0 |
| Receiver Balance Before | 0 |
| Receiver Balance After | 0 |

---

## API Reference

### POST /predict

Analyzes a transaction and returns a fraud prediction.

**Request Body**
```json
{
  "amount": 5000.00,
  "oldbalanceOrg": 20000.00,
  "newbalanceOrig": 15000.00,
  "oldbalanceDest": 1000.00,
  "newbalanceDest": 6000.00
}
```

**Response**
```json
{
  "prediction": "Safe",
  "probability": 0.032
}
```

### GET /health

Returns API and model status.

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

## MLflow Experiment Tracking

MLflow tracks every training run automatically. View the dashboard at:

```
http://localhost:5001
```

Metrics tracked per run:
- Accuracy
- Precision
- Recall
- F1 Score

---

## Retrain the Model on Real Data

1. Download the PaySim dataset from Kaggle:
   [PaySim Synthetic Financial Dataset](https://www.kaggle.com/datasets/ealaxi/paysim1)

2. Rename the file to `paysim.csv` and place it in the `data/` folder

3. Retrain:
```bash
venv\Scripts\python.exe model/train.py
```

4. Upload new model to S3 (for production):
```bash
aws s3 cp model_artifacts/model.joblib s3://<your-bucket>/model_artifacts/model.joblib
```

5. Force ECS to redeploy and pick up the new model:
```bash
aws ecs update-service --cluster fraud-detection-cluster --service fraud-detection-service --force-new-deployment --region ap-south-1
```

---

## CI/CD Pipeline (GitHub Actions)

Every push to `main` automatically:

1. **Runs tests** — `pytest tests/ -v` must pass
2. **Builds Docker image** — from `Dockerfile`
3. **Pushes to AWS ECR** — tagged with git commit SHA + `latest`
4. **Deploys to ECS** — force-restarts the running service
5. **Waits for stability** — confirms deployment is healthy

Pipeline config: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |

---

## Cloud Deployment (AWS)

### Services Used

| AWS Service | Purpose |
|---|---|
| S3 | Store `model.joblib` artifact |
| ECR | Store Docker images |
| ECS Fargate | Run the container (serverless) |
| CloudWatch | Container logs and monitoring |

### Manual Deploy Steps

```bash
# 1. Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# 2. Build image
docker build -t fraud-detection-app .

# 3. Tag and push
docker tag fraud-detection-app:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection-app:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection-app:latest
```

### Environment Variables (ECS Task)

| Variable | Value |
|---|---|
| `S3_BUCKET` | Your S3 bucket name |
| `S3_MODEL_KEY` | `model_artifacts/model.joblib` |
| `AWS_REGION` | `ap-south-1` |
