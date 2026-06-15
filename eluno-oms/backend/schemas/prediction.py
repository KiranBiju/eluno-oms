from datetime import datetime

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    id: int
    order_id: int
    breach_probability: float
    predicted_at: datetime
    risk_level: str
    customer_name: str | None = None
    status: str | None = None
    lens_type: str | None = None

    model_config = {"from_attributes": True}


class PredictionRunResponse(BaseModel):
    orders_scored: int
    high_risk_count: int
    alerts_triggered: int
