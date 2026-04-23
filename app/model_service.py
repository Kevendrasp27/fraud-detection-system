import os
import io
import joblib
import boto3
import pandas as pd
import asyncio
from app.schemas import TransactionInput, PredictionOutput

class ModelService:
    def __init__(self, model_path: str):
        s3_bucket = os.getenv("S3_BUCKET")
        s3_key    = os.getenv("S3_MODEL_KEY", "model_artifacts/model.joblib")

        if s3_bucket:
            # Production: download model from S3
            s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))
            buffer = io.BytesIO()
            s3.download_fileobj(s3_bucket, s3_key, buffer)
            buffer.seek(0)
            self.model = joblib.load(buffer)
        else:
            # Local development: load from disk
            self.model = joblib.load(model_path)

    async def predict(self, transaction: TransactionInput) -> PredictionOutput:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._predict_sync, transaction)

    def _predict_sync(self, transaction: TransactionInput) -> PredictionOutput:
        data = pd.DataFrame([transaction.model_dump()])
        prob = self.model.predict_proba(data)[0][1]
        pred = "Fraud" if prob > 0.5 else "Safe"
        return PredictionOutput(prediction=pred, probability=float(prob))
