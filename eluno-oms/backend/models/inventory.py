from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sphere: Mapped[float] = mapped_column(Float, nullable=False)
    cylinder: Mapped[float] = mapped_column(Float, default=0.0)
    axis: Mapped[int] = mapped_column(Integer, default=0)
    lens_type: Mapped[str] = mapped_column(String(50), nullable=False)
    lens_index: Mapped[str] = mapped_column(String(20), nullable=False)
    coating: Mapped[str] = mapped_column(String(50), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    vendor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
