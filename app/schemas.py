from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    amount: float = Field(..., gt=0)
    oldbalanceOrg: float = Field(..., ge=0)
    newbalanceOrig: float = Field(..., ge=0)
    oldbalanceDest: float = Field(..., ge=0)
    newbalanceDest: float = Field(..., ge=0)

class PredictionOutput(BaseModel):
    prediction: str
    probability: float
