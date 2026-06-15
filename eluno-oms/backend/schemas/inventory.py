from datetime import datetime

from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    sphere: float = Field(..., ge=-20.0, le=20.0)
    cylinder: float = Field(default=0.0, ge=-10.0, le=10.0)
    axis: int = Field(default=0, ge=0, le=180)
    lens_type: str
    lens_index: str
    coating: str
    stock_quantity: int = Field(default=0, ge=0)
    vendor_name: str


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    sphere: float | None = Field(default=None, ge=-20.0, le=20.0)
    cylinder: float | None = Field(default=None, ge=-10.0, le=10.0)
    axis: int | None = Field(default=None, ge=0, le=180)
    lens_type: str | None = None
    lens_index: str | None = None
    coating: str | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    vendor_name: str | None = None


class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AvailabilityRequest(BaseModel):
    sphere: float
    cylinder: float = 0.0
    axis: int = 0
    lens_type: str
    coating: str


class AvailabilityResponse(BaseModel):
    availability: str
    estimated_tat_days: int
    in_stock: bool
    stock_quantity: int = 0
