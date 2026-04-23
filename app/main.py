import time
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import TransactionInput, PredictionOutput
from app.model_service import ModelService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "model_artifacts", "model.joblib")
    model_service = ModelService(model_path)
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model_service = None

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"message": "Internal server error"})

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": model_service is not None
    }

@app.post("/predict", response_model=PredictionOutput)
async def predict_fraud(transaction: TransactionInput):
    if not model_service:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        return await model_service.predict(transaction)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail="Error processing prediction")
