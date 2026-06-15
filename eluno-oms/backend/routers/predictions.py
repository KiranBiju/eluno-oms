"""Predictions API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.prediction import PredictionResponse, PredictionRunResponse
from backend.services import prediction_service

router = APIRouter()


@router.get("/", response_model=list[PredictionResponse])
def list_predictions(limit: int = 100, db: Session = Depends(get_db)):
    return prediction_service.get_all_predictions(db, limit=limit)


@router.post("/run", response_model=PredictionRunResponse)
def run_predictions(db: Session = Depends(get_db)):
    result = prediction_service.run_predictions(db)
    return PredictionRunResponse(**result)
