"""Eluno OMS FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.session import Base, engine
from backend.routers import alerts, copilot, inventory, orders, predictions

# Ensure data directory exists
Path("data").mkdir(exist_ok=True)
Path("data/models").mkdir(exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Eluno OMS API",
    description="AI-Powered Order Management System for Eluno Eyewear",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(copilot.router, prefix="/copilot", tags=["Copilot"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "Eluno OMS"}
