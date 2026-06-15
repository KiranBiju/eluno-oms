from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    store_location: Mapped[str] = mapped_column(String(100), nullable=False)
    sphere: Mapped[float] = mapped_column(Float, nullable=False)
    cylinder: Mapped[float] = mapped_column(Float, default=0.0)
    axis: Mapped[int] = mapped_column(Integer, default=0)
    lens_type: Mapped[str] = mapped_column(String(50), nullable=False)
    lens_index: Mapped[str] = mapped_column(String(20), nullable=False)
    coating: Mapped[str] = mapped_column(String(50), nullable=False)
    frame_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Order Placed")
    sla_days: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_delivery: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    status_history = relationship("StatusHistory", back_populates="order", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="order", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="order", cascade="all, delete-orphan")
