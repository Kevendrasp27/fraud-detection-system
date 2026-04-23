# Fraud Detection System

A production-ready Machine Learning web application that detects fraudulent financial transactions in real time.

**Made by KEVENDRA SINGH PARIHAR**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Machine Learning | Python, Scikit-learn, Pandas, Numpy |
| Experiment Tracking | MLflow |
| Backend API | FastAPI, Uvicorn, Pydantic |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Containerization | Docker, Docker Compose |
| Cloud | AWS (S3, ECR, ECS) |

---

## Project Structure

```
fraud_detection/
├── app/
│   ├── main.py            # FastAPI app — routes, middleware
│   ├── model_service.py   # Loads model, runs predictions
│   └── schemas.py         # Request/response data shapes
├── model/
│   └── train.py           # ML training script
├── model_artifacts/
│   └── model.joblib       # Trained model (binary)
├── frontend/
│   ├── index.html         # UI
│   ├── style.css          # Styling
│   └── script.js          # API calls + animations
├── data/
│   └── paysim.csv         # Transaction dataset
├── Dockerfile             # App container recipe
├── docker-compose.yml     # Runs all 3 services together
├── nginx.conf             # Serves frontend via nginx
├── requirements.txt       # Python dependencies
└── README.md
```

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

> If `data/paysim.csv` is missing, the script auto-generates dummy data so you can test immediately.

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
| Interactive API Docs | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

---

## Option 2 — Run with Docker (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Start all services with one command

```bash
cd fraud_detection
docker-compose up --build
```

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

## Retrain the Model on Real Data

1. Download the PaySim dataset from Kaggle:
   [PaySim Synthetic Financial Dataset](https://www.kaggle.com/datasets/ealaxi/paysim1)

2. Rename the file to `paysim.csv` and place it in the `data/` folder

3. Retrain:
```bash
venv\Scripts\python.exe model/train.py
```

4. Restart the API — it will load the new model automatically

---

## MLflow Experiment Tracking

View all training runs, metrics, and model versions at:

```
http://localhost:5001
```

Metrics tracked per run:
- Accuracy
- Precision
- Recall
- F1 Score

---

## Cloud Deployment (AWS)

### Prerequisites
- AWS CLI installed and configured (`aws configure`)
- Docker Desktop running

### Services Used
| AWS Service | Purpose |
|---|---|
| S3 | Store model.joblib |
| ECR | Store Docker images |
| ECS Fargate | Run the container on the cloud |
| CloudWatch | Logs and monitoring |

### Deploy steps

```bash
# 1. Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# 2. Build image
docker build -t fraud-detection-app .

# 3. Tag image
docker tag fraud-detection-app:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection-app:latest

# 4. Push to ECR
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection-app:latest
```
