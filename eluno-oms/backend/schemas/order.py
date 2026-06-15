from datetime import datetime

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    store_location: str
    sphere: float = Field(..., ge=-20.0, le=20.0)
    cylinder: float = Field(default=0.0, ge=-10.0, le=10.0)
    axis: int = Field(default=0, ge=0, le=180)
    lens_type: str
    lens_index: str
    coating: str
    frame_name: str = Field(..., min_length=1, max_length=100)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=1, max_length=100)
    customer_phone: str | None = Field(default=None, min_length=10, max_length=20)
    store_location: str | None = None
    sphere: float | None = Field(default=None, ge=-20.0, le=20.0)
    cylinder: float | None = Field(default=None, ge=-10.0, le=10.0)
    axis: int | None = Field(default=None, ge=0, le=180)
    lens_type: str | None = None
    lens_index: str | None = None
    coating: str | None = None
    frame_name: str | None = None


class StatusUpdate(BaseModel):
    new_status: str
    reason: str | None = None


class SLAMetrics(BaseModel):
    sla_days: int
    days_elapsed: int
    time_remaining_days: int
    sla_health: str
    expected_delivery: datetime
    delay_reason: str | None = None


class OrderResponse(OrderBase):
    id: int
    status: str
    sla_days: int
    expected_delivery: datetime
    created_at: datetime
    updated_at: datetime
    sla_metrics: SLAMetrics | None = None
    breach_probability: float | None = None
    risk_level: str | None = None

    model_config = {"from_attributes": True}


class StatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    old_status: str
    new_status: str
    reason: str | None
    changed_at: datetime

    model_config = {"from_attributes": True}
