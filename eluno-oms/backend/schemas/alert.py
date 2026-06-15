from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    order_id: int
    alert_type: str
    message: str
    created_at: datetime
    customer_name: str | None = None
    order_status: str | None = None

    model_config = {"from_attributes": True}
